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

namespace TestProject1
{
    public class GamesControllerTests
    {
        private readonly DbContextOptions<GOBContext> _options;

        public GamesControllerTests()
        {
            _options = new DbContextOptionsBuilder<GOBContext>()
                .UseInMemoryDatabase(databaseName: "TestGamesDatabase")
                .Options;
        }

        [Fact]
        public async Task GetGames_ReturnsOkResultWithGameDTOs()
        {
            using (var context = new GOBContext(_options))
            {
                // Arrange
                context.Games.RemoveRange(context.Games);
                context.SaveChanges();

                context.Games.Add(new Game { Game_ID = 1, Home_ID = 1, Away_ID = 2, Game_Date = DateTime.Now });
                context.Games.Add(new Game { Game_ID = 2, Home_ID = 3, Away_ID = 4, Game_Date = DateTime.Now.AddDays(1) });
                context.SaveChanges();

                var controller = new GamesController(context);

                // Act
                var result = await controller.GetGames();

                // Assert
                var okResult = Assert.IsType<OkObjectResult>(result.Result);
                var games = Assert.IsAssignableFrom<IEnumerable<GameDTO>>(okResult.Value);
                Assert.Equal(2, games.Count());
                Assert.Equal(1, games.First().Game_ID);
            }
        }

        [Fact]
        public async Task GetGame_ReturnsOkResultWithGameDTO_WhenIdExists()
        {
            using (var context = new GOBContext(_options))
            {
                // Arrange
                context.Games.RemoveRange(context.Games);
                context.SaveChanges();

                context.Games.Add(new Game { Game_ID = 1, Home_ID = 1, Away_ID = 2, Game_Date = DateTime.Now });
                context.SaveChanges();

                var controller = new GamesController(context);

                // Act
                var result = await controller.GetGame(1);

                // Assert
                var okResult = Assert.IsType<OkObjectResult>(result.Result);
                var game = Assert.IsType<GameDTO>(okResult.Value);
                Assert.Equal(1, game.Game_ID);
            }
        }

        [Fact]
        public async Task GetGame_ReturnsNotFound_WhenIdDoesNotExist()
        {
            using (var context = new GOBContext(_options))
            {
                // Arrange
                var controller = new GamesController(context);

                // Act
                var result = await controller.GetGame(99);

                // Assert
                Assert.IsType<NotFoundResult>(result.Result);
            }
        }

        [Fact]
        public async Task PostGame_ReturnsCreatedAtRouteResult_WhenGameIsCreated()
        {
            using (var context = new GOBContext(_options))
            {
                // Arrange
                context.Teams.RemoveRange(context.Teams); 
                context.SaveChanges();

                context.Teams.Add(new Team { Team_ID = 1, Team_Name = "Home Team", Team_City = "Home City" });
                context.Teams.Add(new Team { Team_ID = 2, Team_Name = "Away Team", Team_City = "Away City" });
                context.SaveChanges();

                var controller = new GamesController(context);
                var gameDto = new GameCreateDTO { Home_ID = 1, Away_ID = 2, Game_Date = DateTime.Now };

                // Act
                var result = await controller.PostGame(gameDto);

                // Assert
                var createdAtRouteResult = Assert.IsType<CreatedAtRouteResult>(result.Result);
                Assert.Equal("GetGame", createdAtRouteResult.RouteName);
                Assert.NotNull(createdAtRouteResult.RouteValues);
                Assert.True(context.Games.Any());
            }
        }

        [Fact]
        public async Task PostGame_ReturnsBadRequest_WhenHomeTeamDoesNotExist()
        {
            using (var context = new GOBContext(_options))
            {
                // Arrange
                context.Teams.RemoveRange(context.Teams); 
                context.SaveChanges();

                context.Teams.Add(new Team { Team_ID = 2, Team_Name = "Away Team", Team_City = "Away City" });
                context.SaveChanges();

                var controller = new GamesController(context);
                var gameDto = new GameCreateDTO { Home_ID = 1, Away_ID = 2, Game_Date = DateTime.Now };

                // Act
                var result = await controller.PostGame(gameDto);

                // Assert
                Assert.IsType<BadRequestObjectResult>(result.Result);
            }
        }

        [Fact]
        public async Task PostGame_ReturnsBadRequest_WhenAwayTeamDoesNotExist()
        {
            using (var context = new GOBContext(_options))
            {
                // Arrange
                context.Teams.RemoveRange(context.Teams); 
                context.SaveChanges();

                context.Teams.Add(new Team { Team_ID = 1, Team_Name = "Home Team", Team_City = "Home City" });
                context.SaveChanges();

                var controller = new GamesController(context);
                var gameDto = new GameCreateDTO { Home_ID = 1, Away_ID = 2, Game_Date = DateTime.Now };

                // Act
                var result = await controller.PostGame(gameDto);

                // Assert
                Assert.IsType<BadRequestObjectResult>(result.Result);
            }
        }

        [Fact]
        public async Task DeleteGame_ReturnsNoContentResult_WhenGameIsDeleted()
        {
            using (var context = new GOBContext(_options))
            {
                // Arrange
                context.Games.RemoveRange(context.Games);
                context.SaveChanges();

                context.Games.Add(new Game { Game_ID = 1, Home_ID = 1, Away_ID = 2, Game_Date = DateTime.Now });
                context.SaveChanges();

                var controller = new GamesController(context);

                // Act
                var result = await controller.DeleteGame(1);

                // Assert
                Assert.IsType<NoContentResult>(result);
                Assert.False(context.Games.Any());
            }
        }

        [Fact]
        public async Task DeleteGame_ReturnsNotFoundResult_WhenGameDoesNotExist()
        {
            using (var context = new GOBContext(_options))
            {
                // Arrange
                var controller = new GamesController(context);

                // Act
                var result = await controller.DeleteGame(99);

                // Assert
                Assert.IsType<NotFoundResult>(result);
            }
        }
    }
}