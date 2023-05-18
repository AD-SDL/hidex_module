using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Project1.ServiceReference1;
using System.Net.Sockets;
using Newtonsoft.Json;
namespace ServiceR
{
    public class Message
    {
        public string action_handle { get; set; }
        
        public Dictionary<string, string> action_vars { get; set; }
    }

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
            Project1.ServiceReference1.HidexSenseAutomationServiceClient client = new Project1.ServiceReference1.HidexSenseAutomationServiceClient(new System.ServiceModel.InstanceContext(new test()));
            try
            {
                //Step 1: Create an instance of the WCF proxy.
               
                client.Connect(false);
                Project1.ServiceReference1.InstrumentState s = client.GetState();
                Console.WriteLine(s);
                //client.OpenPlateCarrier() ;
                // Step 2: Call the service operations.
                // Call the Add service operation.


                // Step 3: Close the client to gracefully close the connection and clean up resources.
                Console.WriteLine("\nPress <Enter> to terminate the client.");
                while (s == InstrumentState.Unknown)
                {
                  s = client.GetState();
                  Console.Out.WriteLine("waiting");
                }






                Socket socket = new Socket(SocketType.Stream, ProtocolType.Tcp);
                socket.Connect("127.0.0.1", 1003);

                // Send the request.
                // For the tiny amount of data in this example, the first call to Send() will likely deliver the buffer completely,
                // however this is not guaranteed to happen for larger real-life buffers.
                // The best practice is to iterate until all the data is sent.

                // Do minimalistic buffering assuming ASCII response
                byte[] responseBytes = new byte[256];
                char[] responseChars = new char[256];
                int c = 0;
                int bytesReceived = 0;
                while (true)
                {
                    bytesReceived = socket.Receive(responseBytes);

                    // Receiving 0 bytes means EOF has been reached
                    if (bytesReceived == 0)
                    {
                        c = c + 1;
                        Console.Out.Write("testasdfsf");
                        break;
                    }
                    // Convert byteCount bytes to ASCII characters using the 'responseChars' buffer as destination
                    int charCount = Encoding.ASCII.GetChars(responseBytes, 0, bytesReceived, responseChars, 0);

                    // Print the contents of the 'responseChars' buffer to Console.Out
                    Console.Out.Write(responseChars, 0, charCount);
                   
                    Message m = JsonConvert.DeserializeObject<Message>(new string(responseChars));
                    Console.Out.Write(m);
                    Console.Out.Write(m.action_handle);
                    Console.Out.Write(m.action_handle == "open");
                    Console.ReadLine();
                    if (m.action_handle == "open")
                    {
                        Console.ReadLine();
                        client.OpenPlateCarrier();
                    }
                    if (m.action_handle == "close")
                    {
                        client.ClosePlateCarrier();
                    }
                    if (m.action_handle == "end")
                    {
                        break;
                    }
                }


            }
            catch(Exception e)
            {
                Console.Out.Write(e);
                Console.ReadLine();
            }
            finally { 
            client.Close();
            }
        }
    }
}
