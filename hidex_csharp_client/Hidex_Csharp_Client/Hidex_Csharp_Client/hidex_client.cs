using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.IO;
using Hidex_Csharp_Client.HidexAutomation;
using System.Net.Sockets;
using System.Net;
using Newtonsoft.Json;
using System.Threading;
namespace ServiceR
{
    public class Message
    {
        public string action_handle { get; set; }

        public Dictionary<string, string> action_vars { get; set; }
    }

    public class Callback_Wrapper : Hidex_Csharp_Client.HidexAutomation.IHidexSenseAutomationServiceCallback
    {
        public void OnStateChanged()
        {
            Console.WriteLine("test");

        }
    }

    class Main_Client
    {
        static void Ping(Hidex_Csharp_Client.HidexAutomation.HidexSenseAutomationServiceClient client)
        {
            InstrumentState hidex_state = client.GetState();
            while (client.GetState() != InstrumentState.Unknown)
            {
                hidex_state = client.GetState();
                Console.Out.WriteLine(hidex_state.ToString());
                Thread.Sleep(1);
            }
        }
        static void Main(string[] args)
        {
            Hidex_Csharp_Client.HidexAutomation.HidexSenseAutomationServiceClient client = new Hidex_Csharp_Client.HidexAutomation.HidexSenseAutomationServiceClient(new System.ServiceModel.InstanceContext(new Callback_Wrapper()));
            try
            {
                //Step 1: Create an instance of the WCF proxy.

                client.Connect(false);
                Hidex_Csharp_Client.HidexAutomation.InstrumentState s = client.GetState();
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

                Thread t = new Thread(() => Ping(client));
                t.Start();


                Socket socket;
                Socket socketo;
                Dns.GetHostEntry("146.137.240.22");
                IPEndPoint T = new IPEndPoint(0, 2000);
                byte[] responseBytes = new byte[256];
                char[] responseChars = new char[256];
                int c = 0;
                int bytesReceived = 0;
                string Path;
                byte[] msg;
                string State;
                socketo = new Socket(SocketType.Stream, ProtocolType.Tcp);
                socketo.Bind(T);
                Dictionary<string, string> response;
                DirectoryInfo dir = new DirectoryInfo("C:\\Users\\PF400\\Documents\\Hidex_Files");
                string fname;
                string firstfname;
                firstfname = dir.GetFiles().OrderByDescending(f => f.LastWriteTime).First().FullName;
                while (true)
                {
                    responseBytes = new byte[256];
                    responseChars = new char[256];
                    socketo.Listen(10000000);
                    socket = socketo.Accept();


                    // Send the request.
                    // For the tiny amount of data in this example, the first call to Send() will likely deliver the buffer completely,
                    // however this is not guaranteed to happen for larger real-life buffers.
                    // The best practice is to iterate until all the data is sent.

                    // Do minimalistic buffering assuming ASCII response


                    {
                        bytesReceived = socket.Receive(responseBytes);
                        try
                        {
                            client.GetState()
                        }
                        catch (Exception e)
                        {
                            client.Close();
                            client.Connect(false);
                        }
                        // Receiving 0 bytes means EOF has been reached
                        if (bytesReceived == 0)
                        {

                            break;
                        }
                        // Convert byteCount bytes to ASCII characters using the 'responseChars' buffer as destination
                        int charCount = Encoding.ASCII.GetChars(responseBytes, 0, bytesReceived, responseChars, 0);

                        // Print the contents of the 'responseChars' buffer to Console.Out
                        Console.Out.Write(responseChars, 0, charCount);
                        Console.Out.Write(responseChars);
                        Message m = JsonConvert.DeserializeObject<Message>(new string(responseChars));
                        Console.Out.Write(m);

                        if (m.action_handle == "open")
                        {
                            client.OpenPlateCarrier();
                            response = new Dictionary<string, string>
                            {
                                { "action_response", "StepStatus.SUCCEEDED" },
                                { "action_msg", "yay" },
                                { "action_log", "birch" }
                            };
                            while (client.GetState() != InstrumentState.Idle) ;
                            msg = Encoding.UTF8.GetBytes(JsonConvert.SerializeObject(response));
                            socket.Send(msg);
                        }
                        else if (m.action_handle == "run_assay")
                        {
                            client.SetAutoExportPath("C:/Users/PF400/Documents/Hidex_Files");
                            client.StartAssay(m.action_vars["assay_name"]);
                            Path = client.GetAutoExportPath();
                            response = new Dictionary<string, string>
                            {
                                { "action_response", "StepStatus.SUCCEEDED" },
                                { "action_log", "birch" }
                            };
                            while (client.GetState() != InstrumentState.Idle) ;
                            fname = dir.GetFiles().OrderByDescending(f => f.LastWriteTime).First().FullName;
                            while (fname == firstfname)
                            {
                                fname = dir.GetFiles().OrderByDescending(f => f.LastWriteTime).First().FullName;
                            }
                            response.Add("action_msg", fname);
                            firstfname = fname;
                            msg = Encoding.UTF8.GetBytes(JsonConvert.SerializeObject(response));
                            socket.Send(msg);

                        }
                        else if (m.action_handle == "close")
                        {
                            client.ClosePlateCarrier();
                            response = new Dictionary<string, string>
                            {
                                { "action_response", "StepStatus.SUCCEEDED" },
                                { "action_msg", "yay" },
                                { "action_log", "birch" }
                            };
                            while (client.GetState() != InstrumentState.Idle) ;
                            msg = Encoding.UTF8.GetBytes(JsonConvert.SerializeObject(response));
                            socket.Send(msg);
                        }


                        else if (m.action_handle == "state")
                        {
                            response = new Dictionary<string, string>
                            {
                                { "action_response", "StepStatus.SUCCEEDED" },
                                { "action_msg", client.GetState().ToString() },
                                { "action_log", "birch" }
                            };

                            msg = Encoding.UTF8.GetBytes(JsonConvert.SerializeObject(response));
                            socket.Send(msg);

                        }
                        else if (m.action_handle == "end")
                        {

                            break;
                        }
                    }
                    socket.Shutdown(SocketShutdown.Both);
                    socket.Disconnect(true);
                    socket.Close();
                }

            }
            catch (Exception e)
            {
                Console.Out.Write(e);
                Console.ReadLine();
            }
            finally
            {
                client.Close();
            }
        }
    }
}
