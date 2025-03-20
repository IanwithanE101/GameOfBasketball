using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using WebApplication1.Database; // Replace with your actual namespace
using WebApplication1.Models; // Replace with your actual namespace
using System.Threading.Tasks;
using WebApplication1.DTOs;

[ApiController]
[Route("[controller]")]
public class TeamsController : ControllerBase
{
    private readonly GOBContext _context;

    public TeamsController(GOBContext context)
    {
        _context = context;
    }

    // GET: api/Teams/5
    [HttpGet("{id}", Name = "GetTeamById")] // Named route
    public async Task<ActionResult<Team>> GetTeam(int id)
    {
        var team = await _context.Teams.FindAsync(id);

        if (team == null)
        {
            return NotFound();
        }

        return team;
    }

    // POST: api/Teams
    [HttpPost]
    public async Task<ActionResult<Team>> PostTeam(TeamCreateDTO teamDto)
    {
        var team = new Team
        {
            Team_Name = teamDto.Team_Name,
            Team_City = teamDto.Team_City
        };

        _context.Teams.Add(team);
        await _context.SaveChangesAsync();

        return CreatedAtRoute("GetTeamById", new { id = team.Team_ID }, team); // Using CreatedAtRoute
    }

    // Other methods (e.g., PUT, DELETE) can be added as needed
}