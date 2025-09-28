using Rag.Candidates.Api.Api.Extensions;

var builder = WebApplication.CreateBuilder(args);

builder.Services
    .AddApplication()
    .AddPresentation();

var app = builder.Build();

app.ConfigureSwagger()
   .MapEndpoints();