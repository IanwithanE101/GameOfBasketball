using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Moq;
using WebApplication1.Controllers; 
using WebApplication1.Database; 
using WebApplication1.Models; 
using WebApplication1.DTOs; 
using Xunit;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using System;

namespace TestProject1 
{
    public class StatControllerTests
    {
        private readonly DbContextOptions<GOBContext> _options;

        public StatControllerTests()
        {
            //Make Database in memory so doesnt effect Actual Database
            _options = new DbContextOptionsBuilder<GOBContext>()
                .UseInMemoryDatabase(databaseName: "TestStatsDatabase")
                .Options;
        }

        [Fact]
        public async Task GetStats_ReturnsOkResultWithStatDTOs()
        {
            using (var context = new GOBContext(_options))
            {
                // Remove Previous Data
                context.Stats.RemoveRange(context.Stats);
                context.SaveChanges();

                //Add Test Data
                context.Stats.Add(new Stat { Stat_ID = 1, Player_ID = 1, Game_ID = 1, Three_Points_Made = 3, Three_Points_Missed = 2, Two_Points_Made = 5, Two_Points_Missed = 1, Free_Throw_Made = 4, Free_Throw_Missed = 0, Steals = 2, Turnovers = 1, Assists = 8, Blocks = 1, Fouls = 3, Off_Rebounds = 2, Def_Rebounds = 5 });
                context.Stats.Add(new Stat { Stat_ID = 2, Player_ID = 2, Game_ID = 2, Three_Points_Made = 2, Three_Points_Missed = 3, Two_Points_Made = 4, Two_Points_Missed = 2, Free_Throw_Made = 3, Free_Throw_Missed = 1, Steals = 1, Turnovers = 2, Assists = 5, Blocks = 0, Fouls = 2, Off_Rebounds = 1, Def_Rebounds = 3 });
                context.SaveChanges();

                // Create Controller
                var controller = new StatsController(context);

                // Function Testing
                var result = await controller.GetStats();

                // Check Results
                var okResult = Assert.IsType<OkObjectResult>(result.Result);
                var stats = Assert.IsAssignableFrom<IEnumerable<StatDTO>>(okResult.Value);
                Assert.Equal(2, stats.Count());
                Assert.Equal(3, stats.First().Three_Points_Made); // Changed assertion
            }
        }

        [Fact]
        public async Task GetStat_ReturnsOkResultWithStatDTO_WhenIdExists()
        {
            using (var context = new GOBContext(_options))
            {
                //Remove all Stats From Previous Tests
                context.Stats.RemoveRange(context.Stats);
                context.SaveChanges();

                //Add Test Data
                context.Stats.Add(new Stat { Stat_ID = 1, Player_ID = 1, Game_ID = 1, Three_Points_Made = 3, Three_Points_Missed = 2, Two_Points_Made = 5, Two_Points_Missed = 1, Free_Throw_Made = 4, Free_Throw_Missed = 0, Steals = 2, Turnovers = 1, Assists = 8, Blocks = 1, Fouls = 3, Off_Rebounds = 2, Def_Rebounds = 5 });
                context.SaveChanges();

                //Controller
                var controller = new StatsController(context);

                //Test
                var result = await controller.GetStat(1);

                //Check
                var okResult = Assert.IsType<OkObjectResult>(result.Result);
                var stat = Assert.IsType<StatDTO>(okResult.Value);
                Assert.Equal(1, stat.Stat_ID);
                Assert.Equal(3, stat.Three_Points_Made);
            }
        }

        [Fact]
        public async Task GetStat_ReturnsNotFound_WhenIdDoesNotExist()
        {
            using (var context = new GOBContext(_options))
            {
                //No need to have data

                //Controller
                var controller = new StatsController(context);

                //Test
                var result = await controller.GetStat(99);

                //Check
                Assert.IsType<NotFoundResult>(result.Result);
            }
        }

        [Fact]
        public async Task PostStat_ReturnsCreatedAtRouteResult_WhenStatIsCreated()
        {
            using (var context = new GOBContext(_options))
            {
                //Clear Data
                context.Stats.RemoveRange(context.Stats);
                context.Players.RemoveRange(context.Players);
                context.Games.RemoveRange(context.Games);
                context.SaveChanges();

                //Add data
                context.Players.Add(new Player { Player_ID = 1, Team_ID = 1, First_Name = "John", Last_Name = "Doe", Position_ID = "C", Jersy_Number = 23 });
                context.Games.Add(new Game { Game_ID = 1, Home_ID = 1, Away_ID = 2, Game_Date = DateTime.Now });
                context.SaveChanges();

                //Controller
                var controller = new StatsController(context);

                //Create temp stat
                var statDto = new StatCreateDTO { Player_ID = 1, Game_ID = 1, Three_Points_Made = 3, Three_Points_Missed = 2, Two_Points_Made = 5, Two_Points_Missed = 1, Free_Throw_Made = 4, Free_Throw_Missed = 0, Steals = 2, Turnovers = 1, Assists = 8, Blocks = 1, Fouls = 3, Off_Rebounds = 2, Def_Rebounds = 5 }; // Using all properties

                // Post
                var result = await controller.PostStat(statDto);

                // Check
                var createdAtRouteResult = Assert.IsType<CreatedAtRouteResult>(result.Result);
                Assert.Equal("GetStat", createdAtRouteResult.RouteName);
                Assert.NotNull(createdAtRouteResult.RouteValues);
                Assert.True(context.Stats.Any());
            }
        }

        [Fact]
        public async Task PostStat_ReturnsBadRequest_WhenPlayerDoesNotExist()
        {
            using (var context = new GOBContext(_options))
            {
                //Remove
                context.Players.RemoveRange(context.Players);
                context.Games.RemoveRange(context.Games);
                context.SaveChanges();

                //add data
                context.Games.Add(new Game { Game_ID = 1, Home_ID = 1, Away_ID = 2, Game_Date = DateTime.Now });
                
                //Controller
                var controller = new StatsController(context);
                
                //Stat with player that doesnt exist
                var statDto = new StatCreateDTO { Player_ID = 99, Game_ID = 1, Three_Points_Made = 3, Three_Points_Missed = 2, Two_Points_Made = 5, Two_Points_Missed = 1, Free_Throw_Made = 4, Free_Throw_Missed = 0, Steals = 2, Turnovers = 1, Assists = 8, Blocks = 1, Fouls = 3, Off_Rebounds = 2, Def_Rebounds = 5 }; // Using all properties

                // Post
                var result = await controller.PostStat(statDto);

                // Check
                Assert.IsType<BadRequestObjectResult>(result.Result);
            }
        }

        [Fact]
        public async Task PostStat_ReturnsBadRequest_WhenGameDoesNotExist()
        {
            using (var context = new GOBContext(_options))
            {
                //Remove
                context.Players.RemoveRange(context.Players);
                context.Games.RemoveRange(context.Games);
                context.SaveChanges();

                //add player
                context.Players.Add(new Player { Player_ID = 1, Team_ID = 1, First_Name = "John", Last_Name = "Doe", Position_ID = "C", Jersy_Number = 23 });

                //Controller
                var controller = new StatsController(context);
                
                //Stat with game that doesnt exist
                var statDto = new StatCreateDTO { Player_ID = 1, Game_ID = 99, Three_Points_Made = 3, Three_Points_Missed = 2, Two_Points_Made = 5, Two_Points_Missed = 1, Free_Throw_Made = 4, Free_Throw_Missed = 0, Steals = 2, Turnovers = 1, Assists = 8, Blocks = 1, Fouls = 3, Off_Rebounds = 2, Def_Rebounds = 5 }; // Using all properties

                // Post
                var result = await controller.PostStat(statDto);

                // Check
                Assert.IsType<BadRequestObjectResult>(result.Result);
            }
        }

        [Fact]
        public async Task DeleteStat_ReturnsNoContentResult_WhenStatIsDeleted()
        {
            using (var context = new GOBContext(_options))
            {
                // Remove
                context.Stats.RemoveRange(context.Stats);
                context.SaveChanges();

                //add
                context.Stats.Add(new Stat { Stat_ID = 1, Player_ID = 1, Game_ID = 1, Three_Points_Made = 3, Three_Points_Missed = 2, Two_Points_Made = 5, Two_Points_Missed = 1, Free_Throw_Made = 4, Free_Throw_Missed = 0, Steals = 2, Turnovers = 1, Assists = 8, Blocks = 1, Fouls = 3, Off_Rebounds = 2, Def_Rebounds = 5 });

                //Controller
                var controller = new StatsController(context);

                // Delete
                var result = await controller.DeleteStat(1);

                // Check
                Assert.IsType<NoContentResult>(result);
                Assert.False(context.Stats.Any());
            }
        }

        [Fact]
        public async Task DeleteStat_ReturnsNotFoundResult_WhenStatDoesNotExist()
        {
            using (var context = new GOBContext(_options))
            {
                // Controller
                var controller = new StatsController(context);

                // Call
                var result = await controller.DeleteStat(99);

                // Check
                Assert.IsType<NotFoundResult>(result);
            }
        }
    }
}