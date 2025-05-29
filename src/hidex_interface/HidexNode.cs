using HidexNode.HidexAutomation;
using System;

namespace HidexNode
{

    public class Callback_Wrapper : IHidexSenseAutomationServiceCallback
    {
        public void OnStateChanged()
        {
            Console.WriteLine("Initialized!");
        }
    }
}