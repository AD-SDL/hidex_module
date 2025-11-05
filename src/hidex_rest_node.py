"""
REST-based node that interfaces with WEI and provides various fake actions for testing purposes
"""

import glob
import os
import time
from pathlib import Path
from typing import Optional

import clr
from madsci.common.types.action_types import ActionCancelled
from madsci.common.types.admin_command_types import AdminCommandResponse
from madsci.common.types.node_types import RestNodeConfig
from madsci.node_module.helpers import action
from madsci.node_module.rest_node_module import RestNode
from typing_extensions import Annotated

clr.AddReference("C:\\Users\\rpl\\\\source\\repos\\hidex_module\\src\\hidex_interface\\bin\\Debug\\HidexNode.dll")
# ruff: noqa: E402
import HidexNode as HN
import HidexNode.HidexAutomation as HA
import System
import System.ServiceModel as SM
import System.ServiceModel.Channels as SMC


class HidexNodeConfig(RestNodeConfig):
    """Configuration for the Hidex REST node"""

    output_path: Optional[str] = "C:\\Users\\rpl\\Desktop\\results"
    """Path to write assay outputs to."""


class HidexNode(RestNode):
    """Hidex Node class for managing the Hidex plate reader"""

    hidex_interface: HA.HidexSenseAutomationServiceClient = None
    config_model = HidexNodeConfig
    config: HidexNodeConfig = HidexNodeConfig()

    # TODO: RESOURCES

    def startup_handler(self) -> None:
        """Called to (re)initialize the node. Should be used to open connections to devices or initialize any other resources."""
        sbe = SMC.ReliableSessionBindingElement()
        binding = SMC.CustomBinding()
        binding.Elements.Add(sbe)
        binding.Elements.Add(SMC.BinaryMessageEncodingBindingElement())
        binding.Elements.Add(SMC.NamedPipeTransportBindingElement())
        self.hidex_interface = HA.HidexSenseAutomationServiceClient(
            SM.InstanceContext(HN.Callback_Wrapper()),
            binding,
            SM.EndpointAddress(System.Uri("net.pipe://localhost/HidexSenseAutomation/")),
        )
        self.hidex_interface.Connect(False)
        state = self.hidex_interface.GetState()
        print(self.hidex_interface.GetState() == state)
        while self.hidex_interface.GetState() == state:
            print(self.hidex_interface.GetState())
            time.sleep(0.5)
        print(self.hidex_interface.GetState())
        self.cancelled = False

    def shutdown_handler(self):
        """Called to shutdown the node. Should be used to close connections to devices or release any other resources."""
        try:
            self.hidex_interface.Disconnect()
            self.shutdown_has_run = True
            del self.ur_interface
            self.hidex_interface = None
        except Exception as err:
            self.logger.log_error(f"Error shutting down the Hidex Node: {err}")
            raise err

    def state_handler(self) -> None:
        """Handles the state of the Hidex node"""
        if not self.hidex_interface:
            self.logger.log_error("Hidex interface is not initialized")
            return

        if self.hidex_interface.GetState() == HA.InstrumentState.Idle:
            self.node_state = {
                "hidex_status_code": "READY",
            }
        elif self.hidex_interface.GetState() == HA.InstrumentState.Busy:
            self.node_state = {
                "hidex_status_code": "BUSY",
            }
            self.logger.info("BUSY")
        else:
            self.node_state = {
                "hidex_status_code": "UNKNOWN",
            }
            self.logger.info("UNKNOWN")

    @action(name="open", description="Open the plate carrier")
    def open(self) -> None:
        """Opens the plate carrier"""
        self.hidex_interface.OpenPlateCarrier()
        time.sleep(1)

    @action(name="close", description="Closes the plate carrier")
    def close(self) -> None:
        """Closes the plate carrier"""
        self.hidex_interface.ClosePlateCarrier()
        time.sleep(1)

    @action(name="run_assay", description="Runs the specificed assay on the current sample")
    def run_assay(
        self,
        assay_name: Annotated[str, "Name of the assay to run"],
        wait_for_result: Annotated[bool, "Whether we should wait for the results of the assay before returning"] = True,
    ) -> Optional[Annotated[Path, "The assay result"]]:
        """Runs assay on the current sample"""

        list_of_files = glob.glob(self.config.output_path + "\\*")  # * means all if need specific format then *.csv
        latest_file = max(list_of_files, key=os.path.getctime)
        prev_file = latest_file
        self.logger.log_info(latest_file)
        self.hidex_interface.SetAutoExportPath(self.config.output_path)
        self.hidex_interface.StartAssay(assay_name)
        while self.hidex_interface.GetState() == HA.InstrumentState.Busy:
            pass
        if bool(wait_for_result) and not self.cancelled:
            while latest_file == prev_file:
                list_of_files = glob.glob(
                    self.config.output_path + "\\*"
                )  # * means all if need specific format then *.csv
                latest_file = max(list_of_files, key=os.path.getctime)
                time.sleep(0.5)
            return Path(latest_file)
        elif self.cancelled:
            self.cancelled = False
            return ActionCancelled()

    def cancel(self) -> AdminCommandResponse:
        """Cancels the current assay"""
        try:
            self.hidex_interface.StopAssay()
            self.cancelled = True
            return AdminCommandResponse(
                success=True,
            )
        except Exception as e:
            self.logger.log_error(f"Error cancelling assay: {e}")
            return AdminCommandResponse(success=False, errors=[e])


if __name__ == "__main__":
    hidex_node = HidexNode()
    hidex_node.start_node()
