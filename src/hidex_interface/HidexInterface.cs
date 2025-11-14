using System;
using HidexInterface.HidexService;

namespace HidexInterface
{
    public class Callback_Wrapper : IHidexSenseAutomationServiceCallback
    {
        public void OnStateChanged()
        {
            Console.WriteLine("State changed in HidexSenseAutomationService.");
        }
    }
}
