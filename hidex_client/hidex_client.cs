﻿using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.IO;
using Hidex_Csharp_Client.HidexAutomation;
using System.Net.Sockets;
using System.Net;
using Newtonsoft.Json;
using System.Threading;
using System.ServiceModel.Channels;
using System.ServiceModel;

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
        static Boolean action_finished = false;
        static Boolean end_called = false;

        static Hidex_Csharp_Client.HidexAutomation.HidexSenseAutomationServiceClient client;

        static void Main(string[] args)
        {
            try
            {

                //Step 1: Create an instance of the WCF proxy.
                ReliableSessionBindingElement sessionBindingElement = new ReliableSessionBindingElement();
                CustomBinding customBinding = new CustomBinding();
                customBinding.Elements.Add((BindingElement)sessionBindingElement);
                customBinding.Elements.Add((BindingElement)new BinaryMessageEncodingBindingElement());
                customBinding.Elements.Add((BindingElement)new NamedPipeTransportBindingElement());
                EndpointAddress remoteAddress = new EndpointAddress(new UriBuilder()
                {
                    Scheme = "net.pipe",
                    Host = "localhost",
                    Path = "HidexSenseAutomation/"
                }.Uri, new AddressHeader[0]);
                client = new HidexSenseAutomationServiceClient(
                    new System.ServiceModel.InstanceContext(new Callback_Wrapper()),
                    (Binding)customBinding,
                    remoteAddress
                );
                client.Connect(false);
                Hidex_Csharp_Client.HidexAutomation.InstrumentState s = client.GetState();
                Console.WriteLine(s);
                // Step 2: Call the service operations.
                // Call the Add service operation.


                // Step 3: Close the client to gracefully close the connection and clean up resources.
                Console.WriteLine("\nPress <Enter> to terminate the client.");
                while (s == InstrumentState.Unknown)
                {
                    s = client.GetState();
                    Console.Out.WriteLine("Initialization: Hidex State Unknown");
                }

                Socket socket;
                Dns.GetHostEntry("146.137.240.22");
                IPEndPoint T = new IPEndPoint(0, 2000);
                byte[] responseBytes = new byte[256];
                char[] responseChars = new char[256];
                int c = 0;
                int bytesReceived = 0;
                string Path;
                byte[] msg;
                Dictionary<string, string> response;
                DirectoryInfo dir = new DirectoryInfo("C:\\labautomation\\data_wei\\proc");
                string fname;
                string firstfname;
                firstfname = dir.GetFiles().OrderByDescending(f => f.LastWriteTime).First().FullName;
                IPAddress allowedIPAddress = IPAddress.Parse("146.137.240.65"); 

                TcpListener tcpListener = new TcpListener(IPAddress.Any, 2000);
                tcpListener.Start();

                while (!(Console.KeyAvailable && Console.ReadKey(true).Key == ConsoleKey.Escape) && !end_called)
                {
                  
                    if (tcpListener.Pending()) {
                        TimeZoneInfo CRtimezone = TimeZoneInfo.FindSystemTimeZoneById("Central Standard Time");
                        Console.WriteLine("Last Socket Connection: " + TimeZoneInfo.ConvertTimeFromUtc(DateTime.UtcNow, CRtimezone));
                        responseBytes = new byte[256];
                        responseChars = new char[256];

                        socket = tcpListener.AcceptSocket();
                        socket.ReceiveTimeout = Timeout.Infinite;
                        socket.SendTimeout = Timeout.Infinite;

                        IPEndPoint remoteEndPoint = (IPEndPoint)socket.RemoteEndPoint;
                        IPAddress remoteIP = remoteEndPoint.Address;
                        int remotePort = remoteEndPoint.Port;
                        Console.WriteLine("Socket Connection Detals. Remote IP Address: " + remoteIP.ToString() + " -- Remote Port Number: " + remotePort);

                        Console.WriteLine("Socket Accepted. Socket Timeout Variable: " + socket.ReceiveTimeout);
                        Console.WriteLine("Available Readable Data Coming from Connnection: " + socket.Available);



                        // Send the request.
                        // For the tiny amount of data in this example, the first call to Send() will likely deliver the buffer completely,
                        // however this is not guaranteed to happen for larger real-life buffers.
                        // The best practice is to iterate until all the data is sent.

                        // Do minimalistic buffering assuming ASCII response

                        if (remoteIP.Equals(allowedIPAddress))
                        {
                            if (socket.Poll(0, SelectMode.SelectRead) && !socket.Poll(0, SelectMode.SelectError))
                            {
                                bytesReceived = socket.Receive(responseBytes);
                                try
                                {
                                    s = client.GetState();
                                    if (client.GetState() == InstrumentState.Unknown)
                                    {
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
                                    TimeZoneInfo central_time = TimeZoneInfo.FindSystemTimeZoneById("Central Standard Time");
                                    Console.WriteLine("From Try Statement on Line 162: " + TimeZoneInfo.ConvertTimeFromUtc(DateTime.UtcNow, central_time));
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
                                    end_called = true;
                                }
                                action_finished = true;

                            }
                            else
                            {
                                if (!socket.Poll(0, SelectMode.SelectRead))
                                {
                                    Console.WriteLine("There was no data to read. Closing socket");
                                    TimeZoneInfo central = TimeZoneInfo.FindSystemTimeZoneById("Central Standard Time");
                                    Console.WriteLine("Instance Occurred: " + TimeZoneInfo.ConvertTimeFromUtc(DateTime.UtcNow, central));
                                }
                                if (socket.Poll(0, SelectMode.SelectError))
                                {
                                    Console.WriteLine("RST packet has been sent to remotely close the socket. Closing socket");
                                    TimeZoneInfo central = TimeZoneInfo.FindSystemTimeZoneById("Central Standard Time");
                                    Console.WriteLine("Instance Occurred: " + TimeZoneInfo.ConvertTimeFromUtc(DateTime.UtcNow, central));
                                }
                            }
                        }
                        else {
                            Console.WriteLine("IP Address of " + remoteIP.ToString() + "trying to send connection to computer. Will not read data because it is not expected IP Address from Potts.");
                        }
                        socket.Shutdown(SocketShutdown.Both);
                        socket.Disconnect(true);
                        socket.Close();
                    }

                    try
                    {
                        if (client.GetState() == InstrumentState.Idle && !action_finished)
                        {
                            Thread.Sleep(5000);
                        }
                    }
                    catch (Exception ex)
                    {
                        TimeZoneInfo CRtimezone = TimeZoneInfo.FindSystemTimeZoneById("Central Standard Time");
                        Console.WriteLine("Error Occurred From Try Statement on Line 314: " + TimeZoneInfo.ConvertTimeFromUtc(DateTime.UtcNow, CRtimezone));
                        Console.Out.WriteLine(ex.ToString());
                    }
                    action_finished = false;
                }

                //End Case: This executes once the escape key is pressed
                client.Disconnect();
                client.Close();

            }
            catch (Exception e)
            {
                TimeZoneInfo CRtimezone = TimeZoneInfo.FindSystemTimeZoneById("Central Standard Time");
                Console.WriteLine("Error Occurred From Try Statement on Line 78: " + TimeZoneInfo.ConvertTimeFromUtc(DateTime.UtcNow, CRtimezone));
                Console.Out.Write(e);
                Console.ReadLine();
            }
        }
    }
}
