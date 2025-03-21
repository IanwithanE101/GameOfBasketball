using Microsoft.EntityFrameworkCore;
using WebApplication1.Database; // Make sure this is the correct namespace
using Microsoft.OpenApi.Models; // Add this using statement

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddControllers();
// Learn more about configuring Swagger/OpenAPI at https://aka.ms/aspnetcore/swashbuckle
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(options =>  // Use options
{
    options.SwaggerDoc("v1", new OpenApiInfo // Add this block
    {
        Title = "Your API Title", // Customize
        Version = "v1",
        Description = "API Description" // Customize
    });
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