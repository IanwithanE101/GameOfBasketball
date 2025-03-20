using Microsoft.AspNetCore.Mvc;
using Microsoft.Data.SqlClient;
using Microsoft.Extensions.Configuration;

[ApiController]
[Route("[controller]")]
public class TestConnectionController : ControllerBase
{
    private readonly IConfiguration _configuration;

    public TestConnectionController(IConfiguration configuration)
    {
        _configuration = configuration;
    }

    [HttpGet]
    public IActionResult TestConnection()
    {
        try
        {
            using (var connection = new SqlConnection(_configuration.GetConnectionString("DefaultConnection")))
            {
                connection.Open();
                using (var command = new SqlCommand("SELECT 1;", connection))
                {
                    var result = command.ExecuteScalar();
                    return Ok($"Connection successful. Result: {result}");
                }
            }
        }
        catch (Exception ex)
        {
            return BadRequest($"Connection failed: {ex.Message}");
        }
    }
}