using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Moq;
using WebApplication1.Controllers; // Replace with your project's namespace
using WebApplication1.Database; // Replace with your project's namespace
using WebApplication1.Models; // Replace with your project's namespace
using WebApplication1.DTOs; // Replace with your project's namespace
using Xunit;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace TestProject1 // Adjust namespace as needed
{
    public class PlayersControllerTests
    {
        private readonly DbContextOptions<GOBContext> _options;

        public PlayersControllerTests()
        {
            _options = new DbContextOptionsBuilder<GOBContext>()
                .UseInMemoryDatabase(databaseName: "TestPlayersDatabase")
                .Options;
        }

        [Fact]
        public async Task GetPlayers_ReturnsOkResultWithPlayerDTOs()
        {
            using (var context = new GOBContext(_options))
            {
                // Arrange
                context.Players.RemoveRange(context.Players); // Clear existing data
                context.SaveChanges();

                context.Players.Add(new Player { Player_ID = 1, Team_ID = 1, First_Name = "John", Last_Name = "Doe", Position_ID = "C", Jersy_Number = 23 });
                context.Players.Add(new Player { Player_ID = 2, Team_ID = 2, First_Name = "Jane", Last_Name = "Smith", Position_ID = "PG", Jersy_Number = 10 });
                context.SaveChanges();

                var controller = new PlayersController(context);

                // Act
                var result = await controller.GetPlayers();

                // Assert
                var okResult = Assert.IsType<OkObjectResult>(result.Result);
                var players = Assert.IsAssignableFrom<IEnumerable<PlayerDTO>>(okResult.Value);
                Assert.Equal(2, players.Count());
                Assert.Equal("John", players.First().First_Name);
            }
        }

        [Fact]
        public async Task GetPlayer_ReturnsOkResultWithPlayerDTO_WhenIdExists()
        {
            using (var context = new GOBContext(_options))
            {
                // Arrange
                context.Players.RemoveRange(context.Players);
                context.SaveChanges();

                context.Players.Add(new Player { Player_ID = 1, Team_ID = 1, First_Name = "John", Last_Name = "Doe", Position_ID = "C", Jersy_Number = 23 });
                context.SaveChanges();

                var controller = new PlayersController(context);

                // Act
                var result = await controller.GetPlayer(1);

                // Assert
                var okResult = Assert.IsType<OkObjectResult>(result.Result);
                var player = Assert.IsType<PlayerDTO>(okResult.Value);
                Assert.Equal(1, player.Player_ID);
                Assert.Equal("John", player.First_Name);
            }
        }

        [Fact]
        public async Task GetPlayer_ReturnsNotFound_WhenIdDoesNotExist()
        {
            using (var context = new GOBContext(_options))
            {
                // Arrange
                context.Players.RemoveRange(context.Players);
                context.SaveChanges();

                // Arrange
                var controller = new PlayersController(context);

                // Act
                var result = await controller.GetPlayer(99);

                // Assert
                Assert.IsType<NotFoundResult>(result.Result);
            }
        }

        [Fact]
        public async Task PostPlayer_ReturnsCreatedAtRouteResult_WhenPlayerIsCreated()
        {
            using (var context = new GOBContext(_options))
            {
                // Arrange
                context.Teams.RemoveRange(context.Teams); // Ensure Teams are clean
                context.SaveChanges();

                context.Teams.Add(new Team { Team_ID = 1, Team_Name = "Test Team", Team_City = "Test City" });
                context.SaveChanges();

                var controller = new PlayersController(context);
                var playerDto = new PlayerCreateDTO { Team_ID = 1, First_Name = "New", Last_Name = "Player", Position_ID = "C", Jersey_Number = 15 };

                // Act
                var result = await controller.PostPlayer(playerDto);

                // Assert
                var createdAtRouteResult = Assert.IsType<CreatedAtRouteResult>(result.Result);
                Assert.Equal("GetPlayerById", createdAtRouteResult.RouteName);
                Assert.NotNull(createdAtRouteResult.RouteValues);
                Assert.True(context.Players.Any());
            }
        }

        [Fact]
        public async Task PostPlayer_ReturnsBadRequest_WhenTeamDoesNotExist()
        {
            using (var context = new GOBContext(_options))
            {
                // Arrange
                context.Teams.RemoveRange(context.Teams); // Ensure Teams are clean
                context.SaveChanges();

                var controller = new PlayersController(context);
                var playerDto = new PlayerCreateDTO { Team_ID = 99, First_Name = "New", Last_Name = "Player", Position_ID = "C", Jersey_Number = 15 };

                // Act
                var result = await controller.PostPlayer(playerDto);

                // Assert
                Assert.IsType<BadRequestObjectResult>(result.Result);
            }
        }

        [Fact]
        public async Task DeletePlayer_ReturnsNoContentResult_WhenPlayerIsDeleted()
        {
            using (var context = new GOBContext(_options))
            {
                // Arrange
                context.Players.RemoveRange(context.Players);
                context.SaveChanges();

                context.Players.Add(new Player { Player_ID = 1, Team_ID = 1, First_Name = "John", Last_Name = "Doe", Position_ID = "C", Jersy_Number = 23 });
                context.SaveChanges();

                var controller = new PlayersController(context);

                // Act
                var result = await controller.DeletePlayer(1);

                // Assert
                Assert.IsType<NoContentResult>(result);
                Assert.False(context.Players.Any());
            }
        }

        [Fact]
        public async Task DeletePlayer_ReturnsNotFoundResult_WhenPlayerDoesNotExist()
        {
            using (var context = new GOBContext(_options))
            {
                // Arrange
                context.Players.RemoveRange(context.Players);
                context.SaveChanges();

                // Arrange
                var controller = new PlayersController(context);

                // Act
                var result = await controller.DeletePlayer(99);

                // Assert
                Assert.IsType<NotFoundResult>(result);
            }
        }
    }
}