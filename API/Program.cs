using Microsoft.EntityFrameworkCore;
using WebApplication1.Database;
using Microsoft.OpenApi.Models;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddControllers();


builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(options => 
{
    options.SwaggerDoc("v1", new OpenApiInfo
    {
        Title = "Game Of Basketball API",
        Version = "v1",
        Description = "A project for Dr. Bilitski's Software engineering class to track, score, and keep track of stats and basketball games"
    });
    options.EnableAnnotations();
});

// Register DbContext
builder.Services.AddDbContext<GOBContext>(options =>
    options.UseSqlServer(builder.Configuration.GetConnectionString("DefaultConnection")));

var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();

app.UseAuthorization();

app.MapControllers();

app.Run();