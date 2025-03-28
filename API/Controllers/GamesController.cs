﻿using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using WebApplication1.Database;
using WebApplication1.Models; 
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using WebApplication1.DTOs;
using Swashbuckle.AspNetCore.Annotations;

namespace WebApplication1.Controllers;

[ApiController]
[Route("[controller]")]
public class GamesController : ControllerBase
{
    private readonly GOBContext _context;

    public GamesController(GOBContext context)
    {
        _context = context;
    }

    // GET: api/Games
    [HttpGet]
    [SwaggerOperation(Summary = "Get All Games", Description = "Retrieves a list of all Games from the database.")]
    public async Task<ActionResult<IEnumerable<GameDTO>>> GetGames()
    {
        try
        {
            var games = await _context.Games
                .Select(g => new GameDTO
                {
                    Game_ID = g.Game_ID,
                    Home_ID = g.Home_ID,
                    Away_ID = g.Away_ID,
                    Game_Date = g.Game_Date,
                })
                .ToListAsync();

            return Ok(games);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error in GetGames: {ex.Message}");
            return StatusCode(500, "Internal Server Error");
        }
    }

    // GET: api/Games/5
    [HttpGet("{id}", Name = "GetGame")]
    [SwaggerOperation(Summary = "Get a Game based on ID", Description = "Retrieves a Game based on ID from the database.")]
    public async Task<ActionResult<GameDTO>> GetGame(int id)
    {
        try
        {
            var game = await _context.Games
                .Select(g => new GameDTO
                {
                    Game_ID = g.Game_ID,
                    Home_ID = g.Home_ID,
                    Away_ID = g.Away_ID,
                    Game_Date = g.Game_Date,
                })
                .FirstOrDefaultAsync(g => g.Game_ID == id);

            if (game == null)
            {
                return NotFound();
            }

            return Ok(game);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error in GetGame: {ex.Message}");
            return StatusCode(500, "Internal Server Error");
        }
    }

    // POST: api/Games
    [HttpPost]
    [SwaggerOperation(Summary = "Create A Game", Description = "Creates a Game and Adds it to the Database.")]
    public async Task<ActionResult<Game>> PostGame(GameCreateDTO gameDto)
    {
        //check if HomeTeam and AwayTeam exists
        var homeTeam = await _context.Teams.FindAsync(gameDto.Home_ID);
        var awayTeam = await _context.Teams.FindAsync(gameDto.Away_ID);

        if (homeTeam == null)
        {
            return BadRequest("Home Team does not exist");
        }

        if (awayTeam == null)
        {
            return BadRequest("Away Team does not exist");
        }
        var game = new Game
        {
            Home_ID = gameDto.Home_ID,
            Away_ID = gameDto.Away_ID,
            Game_Date = gameDto.Game_Date,
        };

        _context.Games.Add(game);
        await _context.SaveChangesAsync();

        return CreatedAtRoute("GetGame", new { id = game.Game_ID }, new GameDTO
        {
            Game_ID = game.Game_ID,
            Home_ID = game.Home_ID,
            Away_ID = game.Away_ID,
            Game_Date = game.Game_Date,
        });
    }

    // DELETE: api/Games/5
    [HttpDelete("{id}")]
    [SwaggerOperation(Summary = "Deletes a Game based on ID", Description = "Deletes a game from the database based on Game_ID.")]
    public async Task<IActionResult> DeleteGame(int id)
    {
        var game = await _context.Games.FindAsync(id);
        if (game == null)
        {
            return NotFound();
        }

        _context.Games.Remove(game);
        await _context.SaveChangesAsync();

        return NoContent();
    }
}