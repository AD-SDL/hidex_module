using Grapevine;
using Hidex_Csharp_Client.HidexAutomation;
using Newtonsoft.Json;
using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net;
using System.Net.Sockets;
using System.ServiceModel;
using System.ServiceModel.Channels;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace ServiceR
{

    public class Callback_Wrapper : Hidex_Csharp_Client.HidexAutomation.IHidexSenseAutomationServiceCallback
    {
        public void OnStateChanged()
        {
            Console.WriteLine("Initialized!");
        }
    }
    [RestResource]
    public class MyResource
    {
        private IRestServer _server;
        public MyResource(IRestServer server)
        {
            _server = server;
        }
        [RestRoute("Get", "/state")]
        public async Task Test(IHttpContext context)
        {


            FileStream fs = File.OpenRead("C:\\Users\\tgins\\Documents\\Book1.xlsx");
            BinaryReader binaryReader = new BinaryReader(fs);
            var Excelbytes = binaryReader.ReadBytes((int)fs.Length);
            if ((bool)_server.Locals["action"] == true)
            {
                _server.Locals.TryUpdate("action", false, true);
            }
            else
            {
                _server.Locals.TryUpdate("action", true, false);

            }
            Thread.Sleep(5000);
            Console.WriteLine(_server.Locals["action"].ToString());
            await context.Response.SendResponseAsync((string)_server.Locals["action"].ToString()).ConfigureAwait(false);
        }
        [RestRoute("Get", "/api/test3")]
        public async Task Test3(IHttpContext context)
        {


            FileStream fs = File.OpenRead("C:\\Users\\tgins\\Documents\\Book1.xlsx");
            BinaryReader binaryReader = new BinaryReader(fs);
            var Excelbytes = binaryReader.ReadBytes((int)fs.Length);

            await context.Response.SendResponseAsync(_server.Locals["action"].ToString()).ConfigureAwait(false);
        }

        [RestRoute("Post", "/action")]
        public async Task action(IHttpContext context)
        {

            string action_handle = context.Request.QueryString["action_handle"];
            string action_vars_string = context.Request.QueryString["action_vars"];
            Dictionary<string, string> action_vars = JsonConvert.DeserializeObject<Dictionary<string, string>>(action_vars_string);
            Hidex_Csharp_Client.HidexAutomation.HidexSenseAutomationServiceClient client;
            client = _server.Locals.GetAs<Hidex_Csharp_Client.HidexAutomation.HidexSenseAutomationServiceClient>("client");

            Dictionary<string, string> response = new Dictionary<string, string>
                                {
                                    { "action_response", "StepStatus.FAILED" },
                                    { "action_msg", "" },
                                    { "action_log", "step timestamp etc" }
                                };
            //context.Response.ContentType = ContentType.Json;

            if ((bool)_server.Locals["action"] == true)
            {


                await context.Response.SendResponseAsync(JsonConvert.SerializeObject(response)).ConfigureAwait(false);
                return;
            }
            if (action_handle == "open")
            {
                _server.Locals.TryUpdate("action", true, false);
                client.OpenPlateCarrier();
                response = new Dictionary<string, string>
                                {
                                    { "action_response", "StepStatus.SUCCEEDED" },
                                    { "action_msg", "" },
                                    { "action_log", "birch" }
                                };
                while (client.GetState() != InstrumentState.Idle) ;
                await context.Response.SendResponseAsync(JsonConvert.SerializeObject(response)).ConfigureAwait(false);
                _server.Locals.TryUpdate("action", false, true);
                return;
            }

            else if (action_handle == "run_assay")
            {
                DirectoryInfo dir = new DirectoryInfo((string)_server.Locals["dir"]);
                _server.Locals.TryUpdate("action", true, false);
                string firstfname = (string)_server.Locals["firstfname"];
                client.SetAutoExportPath("C:\\labautomation\\data_wei\\proc");
                client.StartAssay(action_vars["assay_name"]);
                string Path = client.GetAutoExportPath();
                response = new Dictionary<string, string>
                                {
                                    { "action_response", "StepStatus.SUCCEEDED" },
                                    { "action_log", "birch" }
                                };
                while (client.GetState() != InstrumentState.Idle) ;
                string fname = dir.GetFiles().OrderByDescending(f => f.LastWriteTime).First().FullName;
                while (fname == firstfname)
                {
                    fname = dir.GetFiles().OrderByDescending(f => f.LastWriteTime).First().FullName;
                }
                response.Add("action_msg", fname);
                _server.Locals.TryUpdate("firstfname", fname, firstfname);
                context.Response.Headers.Add("action_response", "StepStatus.SUCCEEDED");
                context.Response.Headers.Add("action_log", "");
                FileStream fs = File.OpenRead(fname);
                BinaryReader binaryReader = new BinaryReader(fs);
                var Excelbytes = binaryReader.ReadBytes((int)fs.Length);
                await context.Response.SendResponseAsync(Excelbytes).ConfigureAwait(false);
                _server.Locals.TryUpdate("action", false, true);
                return;

            }
            else if (action_handle == "close")
            {
                _server.Locals.TryUpdate("action", true, false);
                client.ClosePlateCarrier();
                response = new Dictionary<string, string>
                                {
                                    { "action_response", "StepStatus.SUCCEEDED" },
                                    { "action_msg", "" },
                                    { "action_log", "birch" }
                                };
                while (client.GetState() != InstrumentState.Idle) ;
                await context.Response.SendResponseAsync(JsonConvert.SerializeObject(response)).ConfigureAwait(false);
                _server.Locals.TryUpdate("action", false, true);
                return;
            }
            else
            {
                response = new Dictionary<string, string>
                                {
                                    { "action_response", "StepStatus.FAILED" },
                                    { "action_msg", "" },
                                    { "action_log", "birch" }
                };


                await context.Response.SendResponseAsync(JsonConvert.SerializeObject(response)).ConfigureAwait(false);
                _server.Locals.TryUpdate("action", false, true);
                return;
            }
        }
        class Main_Client
        {


            static Boolean end_called = false;

            static Hidex_Csharp_Client.HidexAutomation.HidexSenseAutomationServiceClient client;

            static void Main(string[] args)
            {


                // Configuration
                const String output_directory = "C:\\labautomation\\data_wei\\proc";
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
                Hidex_Csharp_Client.HidexAutomation.InstrumentState s;
                // client.Connect(false);
                //Hidex_Csharp_Client.HidexAutomation.InstrumentState s = client.GetState();
                //Console.WriteLine("Hidex Client State:");
                //Console.WriteLine(s);

                //Console.Write("Initializing...");
                //while (s == InstrumentState.Unknown)
                // {
                //   Console.Write(".");
                //  s = client.GetState();
                // System.Threading.Thread.Sleep(1000);
                // }
                // Console.WriteLine("Hidex Client State:");
                //Console.WriteLine(s);
                DirectoryInfo dir = new DirectoryInfo(output_directory);

                string firstfname = "";
                //firstfname = dir.GetFiles().OrderByDescending(f => f.LastWriteTime).First().FullName;
                using (var server = RestServerBuilder.UseDefaults().Build())
                {
                    var client_dict = new Dictionary<object, object>()
                {
                    {"client", client }
                };

                    ConcurrentDictionary<object, object> Locals = new ConcurrentDictionary<object, object>(client_dict);
                    var test = new Grapevine.Locals();
                    test.TryAdd("client", client);
                    test.TryAdd("action", false);
                    test.TryAdd("dir", output_directory);
                    test.TryAdd("firstfname", firstfname);
                    server.Locals = test;
                    //server.Prefixes.Add($"http://*:1234/");
                    server.Start();

                    Console.WriteLine("Press enter to stop the server");
                    Console.ReadLine();
                }








            }
        }
    }
}