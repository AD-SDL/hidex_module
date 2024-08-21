

"""
REST-based node that interfaces with WEI and provides various fake actions for testing purposes
"""
import clr
clr.AddReference("C:\\Users\\rpl\\source\\repos\\hidex_module\\hidex_node\\bin\\Debug\\HidexNode.dll")
import System.ServiceModel as SM
import System.ServiceModel.Channels as SMC
import HidexNode.HidexAutomation as HA
import System   
import HidexNode as HN
import time
import glob
import os


print(HA.IHidexSenseAutomationServiceCallback)

from typing import Annotated

from fastapi import UploadFile
from fastapi.datastructures import State
from wei.modules.rest_module import RESTModule
from wei.types import StepFileResponse, StepResponse, StepStatus
from wei.types.module_types import (
    LocalFileModuleActionResult,
    Location,
    ModuleState,
    ValueModuleActionResult,
    ModuleStatus
)
from wei.types.step_types import ActionRequest

# * Test predefined action functions


hidex_rest_node = RESTModule(
    name="hidex_node",
    description="A module to control the Hidex plate reader",
    version="1.0.0",
    resource_pools=[],
    model="Hidex",
    actions=[],
)
hidex_rest_node.arg_parser.add_argument(
    "--output_path",
    type=str,
    help="The starting amount of foo",
    default="C:\\Users\\rpl\\Desktop\\results",
)




@hidex_rest_node.startup()
def test_node_startup(state: State):
    """Initializes the module"""
    sbe = SMC.ReliableSessionBindingElement()
    binding = SMC.CustomBinding()
    binding.Elements.Add(sbe)
    binding.Elements.Add(SMC.BinaryMessageEncodingBindingElement())
    binding.Elements.Add(SMC.NamedPipeTransportBindingElement())
    t = HA.HidexSenseAutomationServiceClient(SM.InstanceContext(HN.Callback_Wrapper()), binding, SM.EndpointAddress(System.Uri("net.pipe://localhost/HidexSenseAutomation/")))
    t.Connect(False)
    c = t.GetState()
    print(t.GetState() == c)
    while t.GetState() == c:
        print(t.GetState())
        time.sleep(0.5)
    print(t.GetState())
    state.client = t
    state.prev_file_name = ""


@hidex_rest_node.state_handler()
def state_handler(state: State) -> ModuleState:
    """Handles the state of the module"""
    if state.client.GetState() == HA.InstrumentState.Idle:
        state.status = ModuleStatus.IDLE
    elif state.client.GetState() == HA.InstrumentState.Busy:
        state.status = ModuleStatus.BUSY
    return ModuleState(status=state.status)




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
def run_assay(state: State, action: ActionRequest,
                   assay_name: Annotated[str, "assay to run"]) -> StepFileResponse:
    """runs assay on the current sample"""

    list_of_files = glob.glob(state.output_path +'\\*') # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)
    print(latest_file)
    state.client.SetAutoExportPath(state.output_path)
    state.client.StartAssay(assay_name)
    while state.client.GetState() == HA.InstrumentState.Busy:
        pass
    while latest_file == state.prev_file_name:
        list_of_files = glob.glob(state.output_path +'\\*') # * means all if need specific format then *.csv
        latest_file = max(list_of_files, key=os.path.getctime)
        time.sleep(0.5)
    state.prev_file_name = latest_file
    return StepFileResponse(
        StepStatus.SUCCEEDED,
        files={"assay_result": latest_file},
    )


if __name__ == "__main__":
    hidex_rest_node.start()

