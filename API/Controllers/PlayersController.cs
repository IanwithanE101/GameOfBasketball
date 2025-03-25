using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using WebApplication1.Database;
using WebApplication1.Models;
using System.Threading.Tasks;
using WebApplication1.DTOs;


[ApiController]
[Route("[controller]")]
public class PlayersController : ControllerBase
{
    private readonly GOBContext _context;

    public PlayersController(GOBContext context)
    {
        _context = context;
    }
    // GET: api/Teams
    [HttpGet]
    public async Task<ActionResult<IEnumerable<Team>>> GetPlayers()
    {
        try
        {
            var players = await _context.Players
                .Select(p => new PlayerDTO
                {
                    Player_ID = p.Player_ID,
                    Team_ID = p.Team_ID,
                    First_Name = p.First_Name,
                    Last_Name = p.Last_Name,
                    Position_ID = p.Position_ID,
                    Jersey_Number = p.Jersy_Number
                })
                .ToListAsync();

            return Ok(players);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error in GetPlayers: {ex.Message}");
            return StatusCode(500, "Internal Server Error");
        }
    }
    // POST: api/Players
    [HttpPost]
    public async Task<ActionResult<Player>> PostPlayer(PlayerCreateDTO playerDto)
    {
        // Check if the team exists
        var team = await _context.Teams.FindAsync(playerDto.Team_ID);
        if (team == null)
        {
            return BadRequest($"Team with ID '{playerDto.Team_ID}' not found.");
        }

        var player = new Player
        {
            Team_ID = playerDto.Team_ID,
            First_Name = playerDto.First_Name,
            Last_Name = playerDto.Last_Name,
            Position_ID = playerDto.Position_ID,
            Jersy_Number = playerDto.Jersey_Number
        };

        _context.Players.Add(player);
        await _context.SaveChangesAsync();

        return CreatedAtRoute("GetPlayerById", new { id = player.Player_ID }, new PlayerDTO
        {
            Player_ID = player.Player_ID,
            Team_ID = player.Team_ID,
            First_Name = player.First_Name,
            Last_Name = player.Last_Name,
            Position_ID = player.Position_ID,
            Jersey_Number = playerDto.Jersey_Number
        });
    }

    // GET: api/Players/5
    [HttpGet("{id}", Name = "GetPlayerById")]
    public async Task<ActionResult<PlayerDTO>> GetPlayer(int id)
    {
        var player = await _context.Players
            .Select(p => new PlayerDTO
            {
                Player_ID = p.Player_ID,
                Team_ID = p.Team_ID,
                First_Name = p.First_Name,
                Last_Name = p.Last_Name,
                Position_ID = p.Position_ID,
                Jersey_Number = p.Jersy_Number
            })
            .FirstOrDefaultAsync(p => p.Player_ID == id);

        if (player == null)
        {
            return NotFound();
        }

        return Ok(player);
    }
    // DELETE: api/Players/5
    [HttpDelete("{id}")]
    public async Task<IActionResult> DeletePlayer(int id)
    {
        // Find the player to delete
        var player = await _context.Players.FindAsync(id);
        if (player == null)
        {
            return NotFound();
        }

        // Remove the player from the context and save changes
        _context.Players.Remove(player);
        await _context.SaveChangesAsync();

        return NoContent();
    }
}