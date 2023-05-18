using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Project1.ServiceReference1;

namespace ServiceR
{
    public class test : Project1.ServiceReference1.IHidexSenseAutomationServiceCallback
    {
       public void OnStateChanged()
        {
            Console.WriteLine("test");
        }
    }
    class Program
    {
        static void Main(string[] args)
        {
            //Step 1: Create an instance of the WCF proxy.
            Project1.ServiceReference1.HidexSenseAutomationServiceClient client = new Project1.ServiceReference1.HidexSenseAutomationServiceClient(new System.ServiceModel.InstanceContext(new test()));
            client.Connect(false);
            Project1.ServiceReference1.InstrumentState s = client.GetState();
            Console.WriteLine(s);
            //client.OpenPlateCarrier() ;
            // Step 2: Call the service operations.
            // Call the Add service operation.
            

            // Step 3: Close the client to gracefully close the connection and clean up resources.
            Console.WriteLine("\nPress <Enter> to terminate the client.");
            Console.ReadLine();
            client.Close();
        }
    }
}
