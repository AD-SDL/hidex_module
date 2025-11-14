"""
REST-based node that interfaces with WEI and provides various fake actions for testing purposes
"""

import os
import time
from pathlib import Path, WindowsPath
from typing import Annotated, Optional

import clr
from madsci.client.resource_client import ResourceClient
from madsci.common.types.action_types import ActionCancelled, ActionFailed, ActionResult, ActionSucceeded
from madsci.common.types.admin_command_types import AdminCommandResponse
from madsci.common.types.node_types import RestNodeConfig
from madsci.node_module.helpers import action
from madsci.node_module.rest_node_module import RestNode

clr.AddReference(str(WindowsPath(__file__).parent / "hidex_interface" / "bin" / "Debug" / "HidexInterface.dll"))
import HidexInterface  # type: ignore  # noqa: E402, I001
import HidexInterface.HidexService as HidexService # type: ignore  # noqa: E402, PLR0402
import System # type: ignore  # noqa: E402
from System import ServiceModel  # type: ignore # noqa: E402
from System.ServiceModel import Channels  # type: ignore # noqa: E402


class HidexNodeConfig(RestNodeConfig):
    """Configuration for the Hidex REST node"""

    output_path: Optional[str] = "C:\\Users\\svcaibio\\Desktop\\results"
    """Path where the Hidex saves assay results"""


class HidexNode(RestNode):
    """Hidex Node class for managing the Hidex plate reader"""

    hidex_interface: HidexService.HidexSenseAutomationServiceClient = None
    """Interface to the Hidex plate reader service"""
    config_model = HidexNodeConfig
    """Configuration model used by the Hidex Node"""
    config: HidexNodeConfig = HidexNodeConfig()
    """Configuration for the Hidex Node"""
    module_version = "1.2.0"
    """Version of the Hidex Node module"""

    def startup_handler(self) -> None:
        """Called to (re)initialize the node. Opens a connection to the Hidex."""

        sbe = Channels.ReliableSessionBindingElement()
        binding = Channels.CustomBinding()
        binding.Elements.Add(sbe)
        binding.Elements.Add(Channels.BinaryMessageEncodingBindingElement())
        binding.Elements.Add(Channels.NamedPipeTransportBindingElement())
        self.hidex_interface = HidexService.HidexSenseAutomationServiceClient(
            ServiceModel.InstanceContext(HidexInterface.Callback_Wrapper()),
            binding,
            ServiceModel.EndpointAddress(System.Uri("net.pipe://localhost/HidexSenseAutomation/")),
        )
        self.hidex_interface.Connect(False)
        state = self.hidex_interface.GetState()
        self.logger.log_debug(self.hidex_interface.GetState() == state)
        while self.hidex_interface.GetState() == state:
            self.logger.log_debug(self.hidex_interface.GetState())
            time.sleep(0.5)
        self.logger.log_debug(self.hidex_interface.GetState())
        self.cancelled = False
        self.logger.log("Hidex node initialized!")

    def shutdown_handler(self) -> None:
        """Called to shutdown the node. Should be used to close connections to devices or release any other resources."""
        self.logger.log("Shutting down")
        self.hidex_interface.Disconnect()
        self.hidex_interface = None
        self.logger.log("Hidex node shutdown successfully!")

    def state_handler(self) -> None:
        """Handles the state of the Hidex node"""
        if not self.hidex_interface or self.node_status.initializing:
            return

        if self.hidex_interface.GetState() == HidexService.InstrumentState.Idle:
            self.node_state = {
                "hidex_status_code": "READY",
            }
        elif self.hidex_interface.GetState() == HidexService.InstrumentState.Busy:
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
        time.sleep(3)
        return ActionSucceeded()

    @action(name="close", description="Closes the plate carrier")
    def close(self) -> None:
        """Closes the plate carrier"""
        self.hidex_interface.ClosePlateCarrier()
        time.sleep(5)
        return ActionSucceeded()

    @action(name="run_assay", description="Runs the specificed assay on the current sample")
    def run_assay(
        self,
        assay_name: Annotated[str, "Name of the assay to run"],
        wait_for_result: Annotated[bool, "Whether we should wait for the results of the assay before returning"] = True,
    ) -> Optional[Annotated[Path, "The assay result"]]:
        """Runs assay on the current sample"""

        self.cancelled = False
        pre_submit_time = time.time()
        self.hidex_interface.SetAutoExportPath(self.config.output_path)
        self.hidex_interface.StartAssay(assay_name)
        while self.hidex_interface.GetState() == HidexService.InstrumentState.Busy:
            pass
        if bool(wait_for_result):
            while not self.cancelled:
                time.sleep(1)
                files = list(Path(self.config.output_path).glob("*"))
                if files:
                    latest_file = max(files, key=os.path.getctime)
                    if latest_file.is_file() and latest_file.stat().st_birthtime > pre_submit_time:
                        break
            else:
                self.logger.log_debug("Assay cancelled before completion")
                return ActionCancelled(errors=["Assay cancelled before completion"])
            return ActionSucceeded(files={"assay_result": latest_file})
        self.cancelled = False
        return ActionSucceeded()

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
