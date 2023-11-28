using Grapevine;
using HidexNode.HidexAutomation;
using McMaster.Extensions.CommandLineUtils;
using System;
using System.IO;
using System.Linq;
using System.ServiceModel;
using System.ServiceModel.Channels;
using System.Threading;

namespace HidexNode
{

    public class Callback_Wrapper : IHidexSenseAutomationServiceCallback
    {
        public void OnStateChanged()
        {
            Console.WriteLine("Initialized!");
        }
    }

    class Program
    {
        public static int Main(string[] args) => CommandLineApplication.Execute<Program>(args);

        ~Program()
        {
            Console.WriteLine("Exiting...");
            client.Disconnect();
            client.Close();
            server.Stop();
        }

        [Option(Description = "Server Hostname")]
        public string Hostname { get; set; } = "+";

        [Option(Description = "Server Port")]
        public int Port { get; } = 2005;

        [Option(Description = "Output Directory")]
        public String OutputPath { get; } = "C:\\labautomation\\data_wei\\proc";

        [Option(Description = "Whether or not to simulate the instrument (note: if the instrument is connected, this does nothing)")]
        public bool Simulate { get; } = true;


        public string state = ModuleStatus.INIT;
        private static HidexSenseAutomationServiceClient client;
        private IRestServer server;
        private DirectoryInfo _output_dir;

        private void OnExecute()
        {
            _output_dir = new DirectoryInfo(OutputPath);

            InitializeHidexClient();

            server = RestServerBuilder.UseDefaults().Build();
            string server_url = "http://" + Hostname + ":" + Port.ToString() + "/";
            Console.WriteLine(server_url);
            server.Prefixes.Clear();
            server.Prefixes.Add(server_url);
            server.Locals.TryAdd("state", state);
            server.Locals.TryAdd("client", client);
            server.Locals.TryAdd("output_path", OutputPath);
            server.Locals.TryAdd("previous_filename", _output_dir.GetFiles().OrderByDescending(f => f.LastWriteTime).First().FullName);
            try
            {
                server.Start();
                Console.WriteLine("Press enter to stop the server");
                Console.ReadLine();
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.ToString());
            }
        }
        private void InitializeHidexClient()
        {
            // Configuration
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
                new InstanceContext(new Callback_Wrapper()),
                (Binding)customBinding,
                remoteAddress
            );
            InstrumentState s;
            client.Connect(Simulate);
            s = client.GetState();
            Console.Write("Hidex Client State: ");
            Console.WriteLine(s);

            Console.Write("Initializing...");
            while (s == InstrumentState.Unknown)
            {
                Console.Write(".");
                s = client.GetState();
                Thread.Sleep(1000);
            }
            Console.Write("Hidex Client State: ");
            Console.WriteLine(s);

            if (s == InstrumentState.Idle)
            {
                state = ModuleStatus.IDLE;
            }
            else
            {
                state = ModuleStatus.ERROR;
            }
        }
    }
}