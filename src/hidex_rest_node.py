"""
REST-based node that interfaces with WEI and provides various fake actions for testing purposes
"""

import clr

clr.AddReference("C:\\Users\\rpl\\\\source\\repos\\hidex_module\\src\\hidex_interface\\bin\\Debug\\HidexNode.dll")
import glob
import os
import time
from typing import Optional, Union
from typing_extensions import Annotated

import HidexNode as HN
import HidexNode.HidexAutomation as HA
import System
import System.ServiceModel as SM
import System.ServiceModel.Channels as SMC
from fastapi.datastructures import State


from madsci.client.resource_client import ResourceClient
from madsci.common.types.action_types import ActionFailed, ActionSucceeded
from madsci.common.types.admin_command_types import AdminCommandResponse
from madsci.common.types.auth_types import OwnershipInfo
from madsci.common.types.location_types import LocationArgument
from madsci.common.types.node_types import RestNodeConfig
from madsci.node_module.helpers import action
from madsci.node_module.rest_node_module import RestNode

from wei.modules.rest_module import RESTModule
from wei.types import StepFileResponse, StepResponse, StepStatus
from wei.types.module_types import (
    LocalFileModuleActionResult,
    ModuleState,
    ModuleStatus,
)
from wei.types.step_types import ActionRequest, StepSucceeded


class HidexNodeConfig(RestNodeConfig):
    """Configuration for the Hidex REST node"""

    output_path: Optional[str] = "C:\\Users\\rpl\\Desktop\\results"

class HidexNode(RestNode):
    """Hidex Node class for managing the Hidex plate reader"""
    hidex_interface: HA.HidexSenseAutomationServiceClient = None
    config_model = HidexNodeConfig

    def startup_handler(self) -> None:
        """Called to (re)initialize the node. Should be used to open connections to devices or initialize any other resources."""
        try: 
            if self.config.resource_server_url:
                self.resource_client = ResourceClient(self.config.resource_server_url)
                self.resource_owner = OwnershipInfo(node_id=self.node_definition.node_id)
            else:
                self.resource_client = None
            self.logger.log("Node initializing...")

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

        except Exception as err:
            self.logger.log_error(f"Error starting the Hidex Node: {err}")
            self.startup_has_run = False
        else:
            self.startup_has_run = True
            self.logger.log("Hidex node initialized!")

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
            
#_#_#_OLD_CODE_#_#_#
hidex_rest_node = RESTModule(
    name="hidex_node",
    description="A module to control the Hidex plate reader",
    version="1.0.0",
    resource_pools=[],
    model="Hidex",
    actions=[],
)


@hidex_rest_node.startup()
def test_node_startup(state: State):
    """Initializes the module"""
    sbe = SMC.ReliableSessionBindingElement()
    binding = SMC.CustomBinding()
    binding.Elements.Add(sbe)
    binding.Elements.Add(SMC.BinaryMessageEncodingBindingElement())
    binding.Elements.Add(SMC.NamedPipeTransportBindingElement())
    t = HA.HidexSenseAutomationServiceClient(
        SM.InstanceContext(HN.Callback_Wrapper()),
        binding,
        SM.EndpointAddress(System.Uri("net.pipe://localhost/HidexSenseAutomation/")),
    )
    t.Connect(False)
    c = t.GetState()
    print(t.GetState() == c)
    while t.GetState() == c:
        print(t.GetState())
        time.sleep(0.5)
    print(t.GetState())
    state.client = t
    state.cancelled = False

@hidex_rest_node.action()
def open(
    state: State,
    action: ActionRequest,
) -> StepResponse:
    """opens plate carrier"""
    state.client.OpenPlateCarrier()
    time.sleep(1)
    return StepResponse.step_succeeded()


@hidex_rest_node.action()
def close(
    state: State,
    action: ActionRequest,
) -> StepResponse:
    """closes plate carrier"""
    state.client.ClosePlateCarrier()
    time.sleep(1)
    return StepResponse.step_succeeded()


@hidex_rest_node.action(
    name="run_assay",
    results=[
        LocalFileModuleActionResult(label="assay_result", description="result file from the assay"),
    ],
)
def run_assay(
    state: State,
    action: ActionRequest,
    assay_name: Annotated[str, "assay to run"],
    wait_for_result: Annotated[bool, "Whether we should wait for the results of the assay before returning"] = True,
) -> StepFileResponse:
    """runs assay on the current sample"""

    list_of_files = glob.glob(state.output_path + "\\*")  # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)
    prev_file = latest_file
    print(latest_file)
    state.client.SetAutoExportPath(state.output_path)
    state.client.StartAssay(assay_name)
    while state.client.GetState() == HA.InstrumentState.Busy:
        pass
    if bool(wait_for_result) and not state.cancelled:
        while latest_file == prev_file:
            list_of_files = glob.glob(state.output_path + "\\*")  # * means all if need specific format then *.csv
            latest_file = max(list_of_files, key=os.path.getctime)
            time.sleep(0.5)
        return StepFileResponse(
            StepStatus.SUCCEEDED,
            files={"assay_result": latest_file},
        )
    else:
        state.cancelled = False
        return StepSucceeded()


@hidex_rest_node.cancel()
def cancel(state: State):
    state.client.StopAssay()
    state.cancelled = True
    state.status = ModuleStatus.IDLE


@hidex_rest_node.shutdown()
def shutdown(state: State):
    state.client.Disconnect()


if __name__ == "__main__":
    hidex_rest_node.start()
