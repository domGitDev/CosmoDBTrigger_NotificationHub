#r "System.Configuration" 
#r "Microsoft.Azure.Documents.Client"
#r "Microsoft.Azure.NotificationHubs"
#r "Newtonsoft.Json"

using System;
using System.Configuration;
using System.Collections.Generic;
using Microsoft.Azure.Documents;
using System.Threading.Tasks;
using Microsoft.Azure.NotificationHubs;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;


public class Notifications
{
    public static Notifications Instance = new Notifications();
    public NotificationHubClient Hub { get; set; }

    string documentDBconnectionString = ConfigurationManager.ConnectionStrings["hubConnectionString"].ConnectionString;
    private string hubNotificationName = ConfigurationManager.ConnectionStrings["notificationHubName"].ConnectionString;

    private Notifications() {
        Hub =  NotificationHubClient.CreateClientFromConnectionString(documentDBconnectionString, hubNotificationName);
    }
}

public static async Task Run(IReadOnlyList<Document> documents, TraceWriter log)
{
    if (documents != null && documents.Count > 0)
    {
        var jsonData = new JObject
        {
            {"aps", new JObject
                {
                    {"alert", ""},
                    {"content-available", 1},
                    {"type", ""}
                }
            }
        };
        var userEmail = documents[0].GetPropertyValue<string>("Email");
        var propModified = documents[0].GetPropertyValue<string>("PropertyModified");

        if(propModified == "Follwing")
        {
            var followers = documents[0].GetPropertyValue<List<string>>(propModified);
            jsonData["aps"]["alert"] = string.Format("@{0} starts following you.", followers.Last());
            jsonData["aps"]["type"] = "Follwing";
        }
        else if(propModified == "UsersLike")
        {
            var usersLike = documents[0].GetPropertyValue<List<string>>(propModified);
            jsonData["aps"]["alert"] = string.Format("@{0} likes your post.", usersLike.Last());
            jsonData["aps"]["type"] = "UsersLike";
        }
        
        log.Verbose("Documents modified " + documents.Count);
        log.Verbose("First document Id " + documents[0].Id);
        await Notifications.Instance.Hub.SendAppleNativeNotificationAsync(jsonData.ToString(), userEmail); 
    }
}
