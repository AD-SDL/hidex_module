"""
MADSci compatible REST node for Hidex Sense Plate Readers.
"""

import os
import time
from pathlib import Path, WindowsPath
from typing import Annotated, Optional

import clr
from madsci.common.types.action_types import (
    ActionCancelled,
    ActionFailed,
)
from madsci.common.types.admin_command_types import AdminCommandResponse
from madsci.common.types.node_types import RestNodeConfig
from madsci.common.types.resource_types import Slot
from madsci.node_module.helpers import action
from madsci.node_module.rest_node_module import RestNode

clr.AddReference(
    str(
        WindowsPath(__file__).parent
        / "hidex_interface"
        / "bin"
        / "Debug"
        / "HidexInterface.dll"
    )
)
import HidexInterface  # type: ignore  # noqa: E402
import HidexInterface.HidexService as HidexService  # type: ignore  # noqa: E402, PLR0402
import System  # type: ignore  # noqa: E402
from System import ServiceModel  # type: ignore # noqa: E402
from System.ServiceModel import Channels  # type: ignore # noqa: E402


class HidexNodeConfig(RestNodeConfig):
    """Configuration for the Hidex REST node"""

    output_path: Path = Path.home() / "Desktop" / "results"
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
        self.initialize_resource_templates()
        self.create_resources()

        sbe = Channels.ReliableSessionBindingElement()
        binding = Channels.CustomBinding()
        binding.Elements.Add(sbe)
        binding.Elements.Add(Channels.BinaryMessageEncodingBindingElement())
        binding.Elements.Add(Channels.NamedPipeTransportBindingElement())
        self.hidex_interface = HidexService.HidexSenseAutomationServiceClient(
            ServiceModel.InstanceContext(HidexInterface.Callback_Wrapper()),
            binding,
            ServiceModel.EndpointAddress(
                System.Uri("net.pipe://localhost/HidexSenseAutomation/")
            ),
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

    def initialize_resource_templates(self) -> None:
        """Initialize the resource templates for the Hidex Node Module"""
        self.resource_client.create_template(
            template_name="hidex.nest",
            description="Plate nest for a Hidex Sense Plate Reader",
            resource=Slot(
                resource_description="Plate nest for a Hidex Node",
            ),
            version="1.0.0",
        )

    def create_resources(self) -> None:
        """Create or attach to the resources for this node"""
        self.resource_client.create_resource_from_template(
            template_name="hidex.nest",
            resource_name=f"{self.node_definition.node_name}.nest",
        )

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

    @action(name="close", description="Closes the plate carrier")
    def close(self) -> None:
        """Closes the plate carrier"""
        self.hidex_interface.ClosePlateCarrier()
        time.sleep(5)

    @action(
        name="run_assay", description="Runs the specificed assay on the current sample"
    )
    def run_assay(
        self,
        assay_name: Annotated[str, "Name of the assay to run"],
        expect_data_file: Annotated[
            bool, "Are you expecting a data file to be returned from this run_assay action?"
        ] = True,
    ) -> Annotated[Optional[Path], "The assay result"]:
        # TODO: Dashboard bug: there's no way to set expect_data_file to False through dashboard..
        """Runs assay on the current sample"""

        self.cancelled = False
        pre_submit_time = time.time()
        self.hidex_interface.SetAutoExportPath(str(self.config.output_path))
        self.hidex_interface.StartAssay(assay_name)
        while self.hidex_interface.GetState() == HidexService.InstrumentState.Busy:
            time.sleep(0.5)

        data_result = None

        while not self.cancelled:
            time.sleep(1)

            self.logger.log_info("Waiting for assay to complete...")
            files = list(Path(self.config.output_path).glob("*"))
            if files:
                latest_file = max(files, key=os.path.getctime)
                if (
                    latest_file.is_file()
                    and latest_file.stat().st_birthtime > pre_submit_time
                ):
                    data_result = Path(latest_file)
                    break
        else:
            self.logger.log_debug("Assay cancelled before completion")
            return ActionCancelled(errors=["Assay cancelled before completion"])

        self.cancelled = False

        # Return None (success) if no data file was expected.
        if not expect_data_file:
            return None

        # If data file was expected but no data_result path found, return ActionFailed.
        if not data_result:
            return ActionFailed(errors=["No data file could be collected."])

        # If data file was expected and data_result path was found but data was never ready, return ActionFailed.
        if not self._wait_until_file_ready(data_result, timeout=600):
            return ActionFailed(errors=["File was never ready (still locked or incomplete)."])

        # Return data_path result if new data was found and is ready.
        return data_result

    def _wait_until_file_ready(
        self,
        file_path: Annotated[Path, "Path to the data file" ],
        timeout: Annotated[int, "Timeout in seconds"] = 600,
        interval: Annotated[int, "Interval in seconds to check if data file is ready"] = 1,
    ) -> bool:
        """
        Waits for the data file to be ready before returning.
        Data from longer assays takes time to populate in the Excel data file.
        """
        start = time.time()
        last_size = -1

        while True:
            try:
                current_size = file_path.stat().st_size

                # Try opening the file (checks lock)
                with open(file_path, "rb"):
                    pass

                # Check if size stopped changing
                if current_size == last_size:
                    return True

                last_size = current_size

            except (PermissionError, FileNotFoundError):
                self.logger.log_info(f"Waiting for data file to be ready. Elapsed time = {int(time.time() - start)} seconds.")

            if time.time() - start > timeout:
                return False

            time.sleep(interval)


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
