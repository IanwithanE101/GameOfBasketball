﻿using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using WebApplication1.Database;
using WebApplication1.Models;
using WebApplication1.DTOs;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Swashbuckle.AspNetCore.Annotations;


[ApiController]
[Route("[controller]")]
public class StatsController : ControllerBase
{
    private readonly GOBContext _context;

    public StatsController(GOBContext context)
    {
        _context = context;
    }

    // GET: api/Stats
    [HttpGet]
    [SwaggerOperation(Summary = "Get All Stats", Description = "Retrieves a list of all Stats from the database.")]
    public async Task<ActionResult<IEnumerable<StatDTO>>> GetStats()
    {
        try
        {
            var stats = await _context.Stats
                .Select(s => new StatDTO
                {
                    Stat_ID = s.Stat_ID,
                    Player_ID = s.Player_ID,
                    Game_ID = s.Game_ID,
                    Three_Points_Made = s.Three_Points_Made,
                    Three_Points_Missed = s.Three_Points_Missed,
                    Two_Points_Made = s.Two_Points_Made,
                    Two_Points_Missed = s.Two_Points_Missed,
                    Free_Throw_Made = s.Free_Throw_Made,
                    Free_Throw_Missed = s.Free_Throw_Missed,
                    Steals = s.Steals,
                    Turnovers = s.Turnovers,
                    Assists = s.Assists,
                    Blocks = s.Blocks,
                    Fouls = s.Fouls,
                    Off_Rebounds = s.Off_Rebounds,
                    Def_Rebounds = s.Def_Rebounds,
                })
                .ToListAsync();

            return Ok(stats);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error in GetStats: {ex.Message}");
            return StatusCode(500, "Internal Server Error");
        }
    } 

    // GET: api/Stats/5
    [HttpGet("{id}", Name = "GetStat")]
    [SwaggerOperation(Summary = "Get a Stat", Description = "Retrieves a Stat from the Database.")]
    public async Task<ActionResult<StatDTO>> GetStat(int id)
    {
        try
        {
            var stat = await _context.Stats
                .Select(s => new StatDTO
                {
                    Stat_ID = s.Stat_ID,
                    Player_ID = s.Player_ID,
                    Game_ID = s.Game_ID,
                    Three_Points_Made = s.Three_Points_Made,
                    Three_Points_Missed = s.Three_Points_Missed,
                    Two_Points_Made = s.Two_Points_Made,
                    Two_Points_Missed = s.Two_Points_Missed,
                    Free_Throw_Made = s.Free_Throw_Made,
                    Free_Throw_Missed = s.Free_Throw_Missed,
                    Steals = s.Steals,
                    Turnovers = s.Turnovers,
                    Assists = s.Assists,
                    Blocks = s.Blocks,
                    Fouls = s.Fouls,
                    Off_Rebounds = s.Off_Rebounds,
                    Def_Rebounds = s.Def_Rebounds,
                })
                .FirstOrDefaultAsync(s => s.Stat_ID == id);

            if (stat == null)
            {
                return NotFound();
            }

            return Ok(stat);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error in GetStat: {ex.Message}");
            return StatusCode(500, "Internal Server Error");
        }
    }

    // GET: api/Stats/Total/Player
    [HttpGet("Player/{playerId}")]
    [SwaggerOperation(Summary = "Get Stats of Player", Description = "Retrieves stats of player from database. All stats are added together from entire database.")]
    public async Task<ActionResult<StatDTO>> GetTotalStatsForPlayer(int playerId)
    {
        try
        {
            var totalStats = await _context.Stats
                .Where(s => s.Player_ID == playerId)
                .GroupBy(s => s.Player_ID)
                .Select(g => new StatDTO
                {
                    Player_ID = g.Key,
                    Three_Points_Made = g.Sum(s => s.Three_Points_Made),
                    Three_Points_Missed = g.Sum(s => s.Three_Points_Missed),
                    Two_Points_Made = g.Sum(s => s.Two_Points_Made),
                    Two_Points_Missed = g.Sum(s => s.Two_Points_Missed),
                    Free_Throw_Made = g.Sum(s => s.Free_Throw_Made),
                    Free_Throw_Missed = g.Sum(s => s.Free_Throw_Missed),
                    Steals = g.Sum(s => s.Steals),
                    Turnovers = g.Sum(s => s.Turnovers),
                    Assists = g.Sum(s => s.Assists),
                    Blocks = g.Sum(s => s.Blocks),
                    Fouls = g.Sum(s => s.Fouls),
                    Off_Rebounds = g.Sum(s => s.Off_Rebounds),
                    Def_Rebounds = g.Sum(s => s.Def_Rebounds),
                })
                .FirstOrDefaultAsync();

            if (totalStats == null)
            {
                return NotFound($"No stats found for player with ID {playerId}");
            }

            return Ok(totalStats);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error in GetTotalStatsForPlayer: {ex.Message}");
            return StatusCode(500, "Internal Server Error");
        }
    }

    // POST: api/Stats
    [HttpPost]
    [SwaggerOperation(Summary = "Add a Stat", Description = "Posts a stat to the database. If that game and player already has a stat, adds stat to already existing stat.")]
    public async Task<ActionResult<Stat>> PostStat(StatCreateDTO statDto)
    {
        // Check if Player_ID and Game_ID exist
        var player = await _context.Players.FindAsync(statDto.Player_ID);
        var game = await _context.Games.FindAsync(statDto.Game_ID);

        if (player == null)
        {
            return BadRequest("Player with given Player_ID does not exist");
        }

        if (game == null)
        {
            return BadRequest("Game with given Game_ID does not exist");
        }

        // Try to find an existing stat for the player and game
        var existingStat = await _context.Stats
            .FirstOrDefaultAsync(s => s.Player_ID == statDto.Player_ID && s.Game_ID == statDto.Game_ID);

        if (existingStat != null)
        {
            // Update the existing stat - INCREMENT the values
            existingStat.Three_Points_Made += statDto.Three_Points_Made;
            existingStat.Three_Points_Missed += statDto.Three_Points_Missed;
            existingStat.Two_Points_Made += statDto.Two_Points_Made;
            existingStat.Two_Points_Missed += statDto.Two_Points_Missed;
            existingStat.Free_Throw_Made += statDto.Free_Throw_Made;
            existingStat.Free_Throw_Missed += statDto.Free_Throw_Missed;
            existingStat.Steals += statDto.Steals;
            existingStat.Turnovers += statDto.Turnovers;
            existingStat.Assists += statDto.Assists;
            existingStat.Blocks += statDto.Blocks;
            existingStat.Fouls += statDto.Fouls;
            existingStat.Off_Rebounds += statDto.Off_Rebounds;
            existingStat.Def_Rebounds += statDto.Def_Rebounds;

            _context.Entry(existingStat).State = EntityState.Modified;
            await _context.SaveChangesAsync();

            return Ok(new StatDTO
            {
                Stat_ID = existingStat.Stat_ID,
                Player_ID = existingStat.Player_ID,
                Game_ID = existingStat.Game_ID,
                Three_Points_Made = existingStat.Three_Points_Made,
                Three_Points_Missed = existingStat.Three_Points_Missed,
                Two_Points_Made = existingStat.Two_Points_Made,
                Two_Points_Missed = existingStat.Two_Points_Missed,
                Free_Throw_Made = existingStat.Free_Throw_Made,
                Free_Throw_Missed = existingStat.Free_Throw_Missed,
                Steals = existingStat.Steals,
                Turnovers = existingStat.Turnovers,
                Assists = existingStat.Assists,
                Blocks = existingStat.Blocks,
                Fouls = existingStat.Fouls,
                Off_Rebounds = existingStat.Off_Rebounds,
                Def_Rebounds = existingStat.Def_Rebounds,
            }); // Return the updated stat
        }
        else
        {
            // Create a new stat
            var stat = new Stat
            {
                Player_ID = statDto.Player_ID,
                Game_ID = statDto.Game_ID,
                Three_Points_Made = statDto.Three_Points_Made,
                Three_Points_Missed = statDto.Three_Points_Missed,
                Two_Points_Made = statDto.Two_Points_Made,
                Two_Points_Missed = statDto.Two_Points_Missed,
                Free_Throw_Made = statDto.Free_Throw_Made,
                Free_Throw_Missed = statDto.Free_Throw_Missed,
                Steals = statDto.Steals,
                Turnovers = statDto.Turnovers,
                Assists = statDto.Assists,
                Blocks = statDto.Blocks,
                Fouls = statDto.Fouls,
                Off_Rebounds = statDto.Off_Rebounds,
                Def_Rebounds = statDto.Def_Rebounds,
            };

            _context.Stats.Add(stat);
            await _context.SaveChangesAsync();

            return CreatedAtRoute("GetStat", new { id = stat.Stat_ID }, new StatDTO 
            {
                Stat_ID = stat.Stat_ID,
                Player_ID = stat.Player_ID,
                Game_ID = stat.Game_ID,
                Three_Points_Made = statDto.Three_Points_Made,
                Three_Points_Missed = statDto.Three_Points_Missed,
                Two_Points_Made = statDto.Two_Points_Made,
                Two_Points_Missed = statDto.Two_Points_Missed,
                Free_Throw_Made = statDto.Free_Throw_Made,
                Free_Throw_Missed = statDto.Free_Throw_Missed,
                Steals = statDto.Steals,
                Turnovers = statDto.Turnovers,
                Assists = statDto.Assists,
                Blocks = statDto.Blocks,
                Fouls = statDto.Fouls,
                Off_Rebounds = statDto.Off_Rebounds,
                Def_Rebounds = statDto.Def_Rebounds,
            });
        }
    }

    // DELETE: api/Stats/5
    [HttpDelete("{id}")]
    [SwaggerOperation(Summary = "Delete stat based on ID", Description = "Removes stat based on Stat ID.")]
    public async Task<IActionResult> DeleteStat(int id)
    {
        var stat = await _context.Stats.FindAsync(id);
        if (stat == null)
        {
            return NotFound();
        }

        _context.Stats.Remove(stat);
        await _context.SaveChangesAsync();

        return NoContent();
    }

    [HttpGet("Game/{gameId}")]
    [SwaggerOperation(Summary = "Get stats for a Game", Description = "Retrieves a list of all player's stats from a specific game from the database.")]
    public async Task<ActionResult<IEnumerable<StatDTO>>> GetStatsForGame(int gameId)
    {
        try
        {
            var gameStats = await _context.Stats
                .Where(s => s.Game_ID == gameId)
                .Select(s => new StatDTO
                {
                    Stat_ID = s.Stat_ID,
                    Player_ID = s.Player_ID,
                    Game_ID = s.Game_ID,
                    Three_Points_Made = s.Three_Points_Made,
                    Three_Points_Missed = s.Three_Points_Missed,
                    Two_Points_Made = s.Two_Points_Made,
                    Two_Points_Missed = s.Two_Points_Missed,
                    Free_Throw_Made = s.Free_Throw_Made,
                    Free_Throw_Missed = s.Free_Throw_Missed,
                    Steals = s.Steals,
                    Turnovers = s.Turnovers,
                    Assists = s.Assists,
                    Blocks = s.Blocks,
                    Fouls = s.Fouls,
                    Off_Rebounds = s.Off_Rebounds,
                    Def_Rebounds = s.Def_Rebounds,
                })
                .ToListAsync();

            if (gameStats == null || !gameStats.Any())
            {
                return NotFound($"No stats found for game with ID {gameId}");
            }

            return Ok(gameStats);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error in GetStatsForGame: {ex.Message}");
            return StatusCode(500, "Internal Server Error");
        }
    }
    
    [HttpGet("GameScore/{gameId}")]
    [SwaggerOperation(Summary = "Get The score of a Game", Description = "Retrieves the score of a specific game based on Game_ID.")]
    public async Task<ActionResult<object>> GetGameScore(int gameId)
    {
        try
        {
            // Fetch the game to get the home and away team IDs
            var game = await _context.Games.FindAsync(gameId);
            if (game == null)
            {
                return NotFound($"Game with ID {gameId} not found");
            }

            // Fetch the stats for the game
            var gameStats = await _context.Stats
                .Where(s => s.Game_ID == gameId)
                .ToListAsync();

            if (gameStats == null || !gameStats.Any())
            {
                return NotFound($"No stats found for game with ID {gameId}");
            }

            // Get the players for the game
            var players = await _context.Players.Where(p => gameStats.Select(s => s.Player_ID).Contains(p.Player_ID)).ToListAsync();

            // Calculate the score for each team
            int homeTeamScore = CalculateTeamScore(gameStats, players, game.Home_ID);
            int awayTeamScore = CalculateTeamScore(gameStats, players, game.Away_ID);

            // Return the result
            return Ok(new
            {
                GameId = gameId,
                HomeTeamScore = homeTeamScore,
                AwayTeamScore = awayTeamScore
            });
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error in GetGameScore: {ex.Message}");
            return StatusCode(500, "Internal Server Error");
        }
    }

    private int CalculateTeamScore(List<Stat> gameStats, List<Player> players, int teamId)
    {
        int score = 0;
        foreach (var stat in gameStats)
        {
            // Find the player associated with this stat
            var player = players.FirstOrDefault(p => p.Player_ID == stat.Player_ID);
            if (player != null && player.Team_ID == teamId)
            {
                score += (stat.Three_Points_Made * 3) + (stat.Two_Points_Made * 2) + stat.Free_Throw_Made;
            }
        }
        return score;
    }

    [HttpGet("Team/{teamId}/Game/{gameId}")]
    [SwaggerOperation(Summary = "Get Stats for Game based on Team", Description = "Retrieves a list of all players stats Based on Team and Game.")]
    public async Task<ActionResult<IEnumerable<StatDTO>>> GetTeamStatsForGame(int teamId, int gameId)
    {
        try
        {
            // Fetch the game to ensure it exists
            var game = await _context.Games.FindAsync(gameId);
            if (game == null)
            {
                return NotFound($"Game with ID {gameId} not found.");
            }

            // Fetch the players for the specified team
            var players = await _context.Players
                .Where(p => p.Team_ID == teamId)
                .ToListAsync();

            if (!players.Any())
            {
                return NotFound($"No players found for team with ID {teamId}.");
            }

            // Get the Player IDs
            var playerIds = players.Select(p => p.Player_ID).ToList();

            // Fetch the stats for the game, filtered by the players of the team
            var teamStats = await _context.Stats
                .Where(s => s.Game_ID == gameId && playerIds.Contains(s.Player_ID))
                .Select(s => new StatDTO
                {
                    Stat_ID = s.Stat_ID,
                    Player_ID = s.Player_ID,
                    Game_ID = s.Game_ID,
                    Three_Points_Made = s.Three_Points_Made,
                    Three_Points_Missed = s.Three_Points_Missed,
                    Two_Points_Made = s.Two_Points_Made,
                    Two_Points_Missed = s.Two_Points_Missed,
                    Free_Throw_Made = s.Free_Throw_Made,
                    Free_Throw_Missed = s.Free_Throw_Missed,
                    Steals = s.Steals,
                    Turnovers = s.Turnovers,
                    Assists = s.Assists,
                    Blocks = s.Blocks,
                    Fouls = s.Fouls,
                    Off_Rebounds = s.Off_Rebounds,
                    Def_Rebounds = s.Def_Rebounds,
                })
                .ToListAsync();

            if (!teamStats.Any())
            {
                return NotFound($"No stats found for team with ID {teamId} in game with ID {gameId}.");
            }

            return Ok(teamStats);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error in GetTeamStatsForGame: {ex.Message}");
            return StatusCode(500, "Internal Server Error");
        }
    }



    [HttpGet("Team/{teamId}/AllTime")]
    [SwaggerOperation(Summary = "Get Total Team Stats", Description = "Retrieves a list of all players stats on a team. Totals all the stats of those players accross all games")]
    public async Task<ActionResult<IEnumerable<StatDTO>>> GetTeamStatsAllTime(int teamId)
    {
        try
        {
            // Fetch the players for the specified team
            var players = await _context.Players
                .Where(p => p.Team_ID == teamId)
                .ToListAsync();

            if (!players.Any())
            {
                return NotFound($"No players found for team with ID {teamId}.");
            }

            // Get the Player IDs
            var playerIds = players.Select(p => p.Player_ID).ToList();

            // Fetch the stats for the players of the team
            var teamStats = await _context.Stats
                .Where(s => playerIds.Contains(s.Player_ID))
                .GroupBy(s => s.Player_ID)
                .Select(g => new StatDTO
                {
                    Player_ID = g.Key,
                    Three_Points_Made = g.Sum(s => s.Three_Points_Made),
                    Three_Points_Missed = g.Sum(s => s.Three_Points_Missed),
                    Two_Points_Made = g.Sum(s => s.Two_Points_Made),
                    Two_Points_Missed = g.Sum(s => s.Two_Points_Missed),
                    Free_Throw_Made = g.Sum(s => s.Free_Throw_Made),
                    Free_Throw_Missed = g.Sum(s => s.Free_Throw_Missed),
                    Steals = g.Sum(s => s.Steals),
                    Turnovers = g.Sum(s => s.Turnovers),
                    Assists = g.Sum(s => s.Assists),
                    Blocks = g.Sum(s => s.Blocks),
                    Fouls = g.Sum(s => s.Fouls),
                    Off_Rebounds = g.Sum(s => s.Off_Rebounds),
                    Def_Rebounds = g.Sum(s => s.Def_Rebounds),
                })
                .ToListAsync();

            if (!teamStats.Any())
            {
                return NotFound($"No stats found for team with ID {teamId}.");
            }

            return Ok(teamStats);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error in GetTeamStatsAllTime: {ex.Message}");
            return StatusCode(500, "Internal Server Error");
        }
    }

}



