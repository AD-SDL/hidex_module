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
    //Wrapper to define how the Automation service handles connections
    public class Callback_Wrapper : Hidex_Csharp_Client.HidexAutomation.IHidexSenseAutomationServiceCallback
    {
        public void OnStateChanged()
        {
            Console.WriteLine("test");

        }
    }

    class Main_Client
    {
        static void Ping_Hidex(Hidex_Csharp_Client.HidexAutomation.HidexSenseAutomationServiceClient client)
        {
            InstrumentState hidex_state = client.GetState();
            while (true)
            {
                try
                {   

                   
                    hidex_state = client.GetState();
                 
                    Thread.Sleep(1000);
                } catch (Exception ex)
                {
                    Console.Out.WriteLine(ex.ToString());
                }
            }
        }
        static void Main(string[] args)
        {
            Hidex_Csharp_Client.HidexAutomation.HidexSenseAutomationServiceClient client = new Hidex_Csharp_Client.HidexAutomation.HidexSenseAutomationServiceClient(new System.ServiceModel.InstanceContext(new Callback_Wrapper()));
            try
            {
                //Connect to the Hidex

                client.Connect(false);
                Hidex_Csharp_Client.HidexAutomation.InstrumentState s = client.GetState();
                
               
              //Wait for connection to verify
               
                while (s == InstrumentState.Unknown)
                {
                    s = client.GetState();
                    Console.Out.WriteLine("waiting");
                }

                Thread ping_hidex = new Thread(() => Ping_Hidex(client));
                ping_hidex.Start();

                //
                Socket socket;
                Socket attach_socket;
               
                IPEndPoint Endpoint = new IPEndPoint(0, 2000);
                byte[] responseBytes = new byte[256];
                char[] responseChars = new char[256];
                
                int bytesReceived = 0;
                string Path;
                byte[] msg;

                attach_socket = new Socket(SocketType.Stream, ProtocolType.Tcp);
                attach_socket.Bind(Endpoint);
                Dictionary<string, string> response;
                DirectoryInfo dir = new DirectoryInfo("C:\\Users\\PF400\\Documents\\Hidex_Files");
                string fname;
                string firstfname;
                firstfname = dir.GetFiles().OrderByDescending(f => f.LastWriteTime).First().FullName;
                while (true)
                {
                 
                    client.Connect(false);
                    responseBytes = new byte[256];
                    responseChars = new char[256];
                    // Read the request.
                    attach_socket.Listen(10000000);
                    //Accept creates a new socket object, that needs to be refreshed.
                    socket = attach_socket.Accept();
                    {
                        bytesReceived = socket.Receive(responseBytes);
                       
                        // Receiving 0 bytes means EOF has been reached
                        if (bytesReceived == 0)
                        {

                            break;
                        }
                        // Convert byteCount bytes to ASCII characters using the 'responseChars' buffer as destination
                        int charCount = Encoding.ASCII.GetChars(responseBytes, 0, bytesReceived, responseChars, 0);

                        //Processed recieved data into Message object
                        Message m = JsonConvert.DeserializeObject<Message>(new string(responseChars));
                        Console.Out.Write(m);
                        //Define Actions
                        if (m.action_handle == "open")
                        {
                            client.OpenPlateCarrier();
                            response = new Dictionary<string, string>
                            {
                                { "action_response", "StepStatus.SUCCEEDED" },
                                { "action_msg", client.GetState().ToString() },
                                { "action_log", "Completed" }
                            };
                            while (client.GetState() != InstrumentState.Idle) ;
                            msg = Encoding.UTF8.GetBytes(JsonConvert.SerializeObject(response));
                            socket.Send(msg);
                        }
                        else if (m.action_handle == "run_assay")
                        {
                            client.SetAutoExportPath("C:\\labautomation\\data_wei\\proc");
                            client.StartAssay(m.action_vars["assay_name"]);
                            Path = client.GetAutoExportPath();
                            response = new Dictionary<string, string>
                            {
                                { "action_response", "StepStatus.SUCCEEDED" },
                                { "action_log", "Completed" }
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
                                { "action_msg",  client.GetState().ToString() },
                                { "action_log", "Completed" }
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
                                { "action_log", "Completed" }
                            };

                            msg = Encoding.UTF8.GetBytes(JsonConvert.SerializeObject(response));
                            socket.Send(msg);

                        }
                        else if (m.action_handle == "end")
                        {

                            break;
                        }
                    }
                    // Step 3: Close the client to gracefully close the connection and clean up resources.
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
