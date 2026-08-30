using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.SignalR;
using Microsoft.Extensions.DependencyInjection;
using System.Text.RegularExpressions;

var builder = WebApplication.CreateBuilder(args);
bool isLocal = false;
if(isLocal)
    builder.WebHost.UseUrls("http://localhost:5000", "https://localhost:5001");
builder.Services.AddSignalR();

// Enable CORS so your desktop app can connect without issues
builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
    {
        policy.AllowAnyHeader()
              .AllowAnyMethod()
              .AllowCredentials()
              .SetIsOriginAllowed(_ => true);
    });
});

var app = builder.Build();
app.UseCors();

app.MapHub<MusicSyncHub>("/syncHub");

app.Run();

// --- Hub Definition ---
public class MusicSyncHub : Hub
{
    public async Task JoinRoom(string roomCode, string userTag)
    {
        await Groups.AddToGroupAsync(Context.ConnectionId, roomCode);
        // Notify others in room that a peer joined
        await Clients.OthersInGroup(roomCode).SendAsync("PeerJoined", userTag);
    }

    public async Task LeaveRoom(string roomCode)
    {
        await Groups.RemoveFromGroupAsync(Context.ConnectionId, roomCode);
        await Clients.OthersInGroup(roomCode).SendAsync("PeerLeft", Context.ConnectionId);
    }

    public async Task SendSyncAction(string roomCode, string messageJson)
    {
        // Broadcast playback action to everyone in the room except the sender
        await Clients.OthersInGroup(roomCode).SendAsync("ReceiveSyncAction", messageJson);
    }
}