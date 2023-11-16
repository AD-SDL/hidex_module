﻿using Grapevine;
using HidexModule.HidexAutomation;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading.Tasks;

namespace HidexNode
{
    [RestResource]
    public class HidexRestServer
    {
        private IRestServer _server;

        public HidexRestServer(IRestServer server)
        {
            _server = server;
        }

        [RestRoute("Get", "/state")]
        public async Task State(IHttpContext context)
        {
            string state = _server.Locals.GetAs<string>("state");
            Dictionary<string, string> response = new Dictionary<string, string>();
            response["State"] = state;
            await context.Response.SendResponseAsync(JsonConvert.SerializeObject(response));
        }

        [RestRoute("Get", "/about")]
        public async Task About(IHttpContext context)
        {
            // TODO
            await context.Response.SendResponseAsync("about");
        }

        [RestRoute("Get", "/resources")]
        public async Task Resources(IHttpContext context)
        {
            // TODO
            await context.Response.SendResponseAsync("resources");
        }

        [RestRoute("Post", "/action")]
        public async Task Action(IHttpContext context)
        {

            string action_handle;
            string action_vars;
            context.Request.PathParameters.TryGetValue("action_handle", out action_handle);
            context.Request.PathParameters.TryGetValue("action_vars", out action_vars);
            Dictionary<string, string> args = JsonConvert.DeserializeObject(action_vars) as Dictionary<string, string>;
            var result = UtilityFunctions.action_response();
            string state = _server.Locals.GetAs<string>("state");
            HidexSenseAutomationServiceClient client = _server.Locals.GetAs<HidexSenseAutomationServiceClient>("client");

            if (state == ModuleStatus.BUSY)
            {
                result = UtilityFunctions.action_response(StepStatus.FAILED, "", "Module is Busy");
                await context.Response.SendResponseAsync(JsonConvert.SerializeObject(result));
            }
            try
            {
                _server.Locals.TryUpdate("state", ModuleStatus.BUSY, _server.Locals.GetAs<string>("state"));
                switch (action_handle)
                {
                    case "open":
                        client.OpenPlateCarrier();
                        while (client.GetState() == InstrumentState.Busy) ;
                        result = UtilityFunctions.action_response(StepStatus.SUCCEEDED, "Opened Hidex", "");
                        break;
                    case "run_assay":
                        string output_path = _server.Locals.GetAs<string>("output_path");
                        DirectoryInfo output_dir = new DirectoryInfo(output_path);
                        string previous_filename = _server.Locals.GetAs<string>("previous_filename");
                        client.SetAutoExportPath(output_path);
                        client.StartAssay(args["assay_name"]);
                        while (client.GetState() == InstrumentState.Busy) ;
                        string filename = output_dir.GetFiles().OrderByDescending(f => f.LastWriteTime).First().FullName;
                        while (filename == previous_filename)
                        {
                            filename = output_dir.GetFiles().OrderByDescending(f => f.LastWriteTime).First().FullName;
                        }
                        _server.Locals.TryUpdate("previous_filename", filename, previous_filename);
                        context.Response.Headers.Add("x-wei-action_response", "StepStatus.SUCCEEDED");
                        context.Response.Headers.Add("x-wei-action_log", "");
                        context.Response.Headers.Add("x-wei-action_msg", filename);
                        FileStream fs = File.OpenRead(filename);
                        BinaryReader binaryReader = new BinaryReader(fs);
                        var Excelbytes = binaryReader.ReadBytes((int)fs.Length);
                        _server.Locals.TryUpdate("state", ModuleStatus.IDLE, _server.Locals.GetAs<string>("state"));
                        await context.Response.SendResponseAsync(Excelbytes);
                        break;
                    case "close":
                        client.ClosePlateCarrier();
                        while (client.GetState() == InstrumentState.Busy) ;
                        result = UtilityFunctions.action_response(StepStatus.SUCCEEDED, "Closed Hidex", "");
                        break;
                    default:
                        Console.WriteLine("Unknown action: " + action_handle);
                        result = UtilityFunctions.action_response(StepStatus.FAILED, "", "Unknown action: " + action_handle);
                        break;
                }
                _server.Locals.TryUpdate("state", ModuleStatus.IDLE, _server.Locals.GetAs<string>("state"));
            }
            catch (Exception ex)
            {
                _server.Locals.TryUpdate("state", ModuleStatus.ERROR, _server.Locals.GetAs<string>("state"));
                Console.WriteLine(ex.ToString());
                result = UtilityFunctions.action_response(StepStatus.FAILED, "", "Step failed: " + ex.ToString());
            }

            await context.Response.SendResponseAsync(JsonConvert.SerializeObject(result));
        }
    }
}
