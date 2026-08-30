# 1. Build stage
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

# Copy the csproj and restore dependencies
COPY *.csproj ./
RUN dotnet restore

# Copy everything else and build the project
COPY . ./
RUN dotnet publish -c Release -o /app/publish

# 2. Runtime stage
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS final
WORKDIR /app
COPY --from=build /app/publish .

# Expose Render's default port
EXPOSE 10000

# Replace 'YourProjectName.dll' with the name of your .csproj (e.g. MyApi.dll)
ENTRYPOINT ["dotnet", "RelayServer.AppHost.dll"]
