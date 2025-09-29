using Rag.Candidates.Api.Extensions;
using Rag.Candidates.Core.Application.UseCases;
using Rag.Candidates.Core.Domain.Configuration;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddConfiguration(builder.Configuration);
builder.Services.AddInfrastructure();
builder.Services.AddApplication();
builder.Services.AddPresentation();

var app = builder.Build();

app.ConfigureSwagger();
app.MapEndpoints();

var buildIndexUseCase = app.Services.GetRequiredService<BuildIndexUseCase>();
await buildIndexUseCase.ExecuteAsync();

var settings = app.Services.GetRequiredService<Settings>();
app.Run(settings.DotnetApi.Urls);