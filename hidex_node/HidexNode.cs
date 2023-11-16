using Grapevine;
using HidexModule.HidexAutomation;
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

        [Option(Description = "Server Port")]
        public int Port { get; } = 2006;

        [Option(Description = "Output Directory")]
        public String output_path { get; } = "C:\\labautomation\\data_wei\\proc";


        public string state = ModuleStatus.INIT;
        private static HidexSenseAutomationServiceClient client;
        private IRestServer server;
        private DirectoryInfo _output_dir;

        private void OnExecute()
        {
            _output_dir = new DirectoryInfo(output_path);

            InitializeHidexClient();

            server = RestServerBuilder.UseDefaults().Build();
            server.Prefixes.Add("http://localhost:" + Port.ToString() + "/");
            server.Locals.TryAdd("state", state);
            server.Locals.TryAdd("client", client);
            server.Locals.TryAdd("output_path", output_path);
            server.Locals.TryAdd("previous_filename", _output_dir.GetFiles().OrderByDescending(f => f.LastWriteTime).First().FullName);
            server.Start();

            Console.WriteLine("Press enter to stop the server");
            Console.ReadLine();
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
            client.Connect(false);
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