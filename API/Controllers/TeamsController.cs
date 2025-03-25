using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using WebApplication1.Database;
using WebApplication1.Models;
using System.Threading.Tasks;
using WebApplication1.DTOs;
using Swashbuckle.AspNetCore.Annotations;


[ApiController]
[Route("[controller]")]
public class TeamsController : ControllerBase
{
    private readonly GOBContext _context;

    public TeamsController(GOBContext context)
    {
        _context = context;
    }

    // GET: api/Teams
    [HttpGet]
    public async Task<ActionResult<IEnumerable<Team>>> GetTeams()
    {
        try
        {
            var teams = await _context.Teams
                .Select(t => new TeamDTO 
                {
                    Team_ID = t.Team_ID,
                    Team_Name = t.Team_Name,
                    Team_City = t.Team_City,
                })
                .ToListAsync();

            return Ok(teams);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error in GetTeams: {ex.Message}");
            return StatusCode(500, "Internal Server Error");
        }
    }

    // GET: api/Teams/5
    [HttpGet("{id}", Name = "GetTeamById")]
    public async Task<ActionResult<Team>> GetTeam(int id)
    {
        var team = await _context.Teams.FindAsync(id);

        if (team == null)
        {
            return NotFound();
        }

        return team;
    }
    // GET: api/Teams/ByName/{teamName}
    [HttpGet("ByName/{teamName}")]
    public async Task<ActionResult<IEnumerable<TeamDTO>>> GetTeamsByName(string teamName)
    {
        try
        {
            var teams = await _context.Teams
                .Where(t => t.Team_Name == teamName)
                .Select(t => new TeamDTO
                {
                    Team_ID = t.Team_ID,
                    Team_Name = t.Team_Name,
                    Team_City = t.Team_City,
                })
                .ToListAsync();

            if (!teams.Any()) 
            {
                return NotFound($"No teams found with the name '{teamName}'.");
            }

            return Ok(teams);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error in GetTeamsByName: {ex.Message}");
            return StatusCode(500, "Internal Server Error");
        }
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

        return CreatedAtRoute("GetTeamById", new { id = team.Team_ID }, team);
    }

    // DELETE: api/Teams/5
    [HttpDelete("{id}")]
    public async Task<IActionResult> DeleteTeam(int id)
    {
        var team = await _context.Teams.FindAsync(id);
        if (team == null)
        {
            return NotFound();
        }

        _context.Teams.Remove(team);
        await _context.SaveChangesAsync();

        return NoContent();
    }
}
