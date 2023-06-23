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
using System.Runtime.InteropServices;

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
        static Boolean action_in_process = false;
        static void Ping_Hidex_State(Hidex_Csharp_Client.HidexAutomation.HidexSenseAutomationServiceClient client)
        {
            while (true)
            {
                if (!action_in_process)
                {
                    try
                    {
                        Thread.Sleep(5000);
                        if (client.GetState() == InstrumentState.Idle)
                        {
               
                            Console.WriteLine("Running Ping Continuously");
                        }

                    }

                    catch (Exception ex)
                    {
                        Console.WriteLine("Catch: In Ping Statement");
                        Console.Out.WriteLine(ex.ToString());
                    }
                }
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
                    Console.Out.WriteLine("Initialization");
                }

                Thread t = new Thread(() => Ping_Hidex_State(client));
                t.Start();

                Socket socket;
                Socket attach_socket;
                Dns.GetHostEntry("146.137.240.22");
                IPEndPoint T = new IPEndPoint(0, 2000);
                byte[] responseBytes = new byte[256];
                char[] responseChars = new char[256];
                int c = 0;
                int bytesReceived = 0;
                string Path;
                byte[] msg;
                attach_socket = new Socket(SocketType.Stream, ProtocolType.Tcp);
                attach_socket.Bind(T);
                Dictionary<string, string> response;
                DirectoryInfo dir = new DirectoryInfo("C:\\labautomation\\data_wei\\proc");
                string fname;
                string firstfname;
                firstfname = dir.GetFiles().OrderByDescending(f => f.LastWriteTime).First().FullName;
                int lastTime = (int)(DateTime.UtcNow - new DateTime(1970, 1, 1)).TotalSeconds;
                while (true)
                {
                    if (client.GetState() == InstrumentState.Idle) {
                        try
                        {
                            InstrumentState hidex_state = client.GetState();
                        }
                        catch (Exception ex)
                        {
                            Console.Out.WriteLine(ex.ToString());
                        }
                    }
                    
                    responseBytes = new byte[256];
                    responseChars = new char[256];
                    attach_socket.Listen(10000000);
                    socket = attach_socket.Accept();

                    Console.WriteLine("Socket Accepted");


                    // Send the request.
                    // For the tiny amount of data in this example, the first call to Send() will likely deliver the buffer completely,
                    // however this is not guaranteed to happen for larger real-life buffers.
                    // The best practice is to iterate until all the data is sent.

                    // Do minimalistic buffering assuming ASCII response


                    {
                        bytesReceived = socket.Receive(responseBytes);
                        try
                        {
                            s = client.GetState();
                            if (client.GetState() == InstrumentState.Unknown) {
                                client.Close();
                                client.Connect(false);
                                Console.WriteLine("Client Connected");
                                s = client.GetState();
                                while (s == InstrumentState.Unknown)
                                {
                                    s = client.GetState();
                                    Console.Out.WriteLine("Try: Instrument State Unknown");
                                }
                            }
                        }
                        catch (Exception e)
                        {
                            client.Close();
                            client.Connect(false);
                            s = client.GetState();
                            while (s == InstrumentState.Unknown)
                            {
                                s = client.GetState();
                                Console.Out.WriteLine("Catch: Instrument State Unknown");
                            }
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
                            action_in_process = true;
                            client.OpenPlateCarrier();
                            response = new Dictionary<string, string>
                            {
                                { "action_response", "StepStatus.SUCCEEDED" },
                                { "action_msg", client.GetState().ToString() },
                                { "action_log", "birch" }
                            };
                            while (client.GetState() != InstrumentState.Idle) ;
                            msg = Encoding.UTF8.GetBytes(JsonConvert.SerializeObject(response));
                            socket.Send(msg);
                            action_in_process = false;
                        }
                        else if (m.action_handle == "run_assay")
                        {
                            action_in_process = true;
                            client.SetAutoExportPath("C:\\labautomation\\data_wei\\proc");
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
                            action_in_process = false;


                        }
                        else if (m.action_handle == "close")
                        {
                            action_in_process = true;
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
                            action_in_process = false;
                        }


                        else if (m.action_handle == "state")
                        {
                            action_in_process = true;
                            response = new Dictionary<string, string>
                            {
                                { "action_response", "StepStatus.SUCCEEDED" },
                                { "action_msg", client.GetState().ToString() },
                                { "action_log", "birch" }
                            };

                            msg = Encoding.UTF8.GetBytes(JsonConvert.SerializeObject(response));
                            socket.Send(msg);
                            action_in_process = false;

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
