using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
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
    public class TeamsControllerTests
    {
        private readonly DbContextOptions<GOBContext> _options;

        public TeamsControllerTests()
        {
            _options = new DbContextOptionsBuilder<GOBContext>()
                .UseInMemoryDatabase(databaseName: "TestTeamsDatabase")
                .Options;
        }

        [Fact]
        public async Task GetTeams_ReturnsOkResultWithTeamDTOs()
        {
            using (var context = new GOBContext(_options))
            {
                // Clear Context for New Test Data
                context.Teams.RemoveRange(context.Teams);
                context.SaveChanges();

                // Arrange
                context.Teams.Add(new Team { Team_ID = 1, Team_Name = "Team A", Team_City = "City A" });
                context.Teams.Add(new Team { Team_ID = 2, Team_Name = "Team B", Team_City = "City B" });
                context.SaveChanges();

                var controller = new TeamsController(context);

                // Act
                var result = await controller.GetTeams();

                // Assert
                var okResult = Assert.IsType<OkObjectResult>(result.Result);
                var teams = Assert.IsAssignableFrom<IEnumerable<TeamDTO>>(okResult.Value);
                Assert.Equal(2, teams.Count());
                Assert.Equal("Team A", teams.First().Team_Name);
            }
        }

        [Fact]
        public async Task GetTeam_ReturnsTeam_WhenIdExists()
        {
            using (var context = new GOBContext(_options))
            {
                // Clear Context for New Test Data
                context.Teams.RemoveRange(context.Teams);
                context.SaveChanges();

                // Arrange
                context.Teams.Add(new Team { Team_ID = 1, Team_Name = "Team A", Team_City = "City A" });
                context.SaveChanges();

                var controller = new TeamsController(context);

                // Act
                var result = await controller.GetTeam(1);

                // Assert
                var team = Assert.IsType<Team>(result.Value);
                Assert.Equal(1, team.Team_ID);
                Assert.Equal("Team A", team.Team_Name);
            }
        }

        [Fact]
        public async Task GetTeam_ReturnsNotFound_WhenIdDoesNotExist()
        {
            using (var context = new GOBContext(_options))
            {
                // Clear Context for New Test Data
                context.Teams.RemoveRange(context.Teams);
                context.SaveChanges();


                // Arrange
                var controller = new TeamsController(context);

                // Act
                var result = await controller.GetTeam(99);

                // Assert
                Assert.IsType<NotFoundResult>(result.Result);
            }
        }

        [Fact]
        public async Task GetTeamsByName_ReturnsOkResultWithTeamDTOs_WhenNameExists()
        {
            using (var context = new GOBContext(_options))
            {
                // Clear Context for New Test Data
                context.Teams.RemoveRange(context.Teams);
                context.SaveChanges();

                // Arrange
                context.Teams.Add(new Team { Team_ID = 1, Team_Name = "Test Team", Team_City = "City A" });
                context.Teams.Add(new Team { Team_ID = 2, Team_Name = "Another Team", Team_City = "City B" });
                context.Teams.Add(new Team { Team_ID = 3, Team_Name = "Test Team", Team_City = "City C" });
                context.SaveChanges();

                var controller = new TeamsController(context);

                // Act
                var result = await controller.GetTeamsByName("Test Team");

                // Assert
                var okResult = Assert.IsType<OkObjectResult>(result.Result);
                var teams = Assert.IsAssignableFrom<IEnumerable<TeamDTO>>(okResult.Value);
                Assert.Equal(2, teams.Count());
                Assert.Contains(teams, t => t.Team_Name == "Test Team");
            }
        }

        [Fact]
        public async Task GetTeamsByName_ReturnsNotFound_WhenNameDoesNotExist()
        {
            using (var context = new GOBContext(_options))
            {
                // Clear Context for New Test Data
                context.Teams.RemoveRange(context.Teams);
                context.SaveChanges();

                // Arrange
                var controller = new TeamsController(context);

                // Act
                var result = await controller.GetTeamsByName("Nonexistent Team");

                // Assert
                var notFoundResult = Assert.IsType<NotFoundObjectResult>(result.Result);
                Assert.Equal("No teams found with the name 'Nonexistent Team'.", notFoundResult.Value);
            }
        }

        [Fact]
        public async Task PostTeam_ReturnsCreatedAtRouteResult_WhenTeamIsCreated()
        {
            using (var context = new GOBContext(_options))
            {
                // Clear Context for New Test Data
                context.Teams.RemoveRange(context.Teams);
                context.SaveChanges();

                // Arrange
                var controller = new TeamsController(context);
                var teamDto = new TeamCreateDTO { Team_Name = "New Team", Team_City = "New City" };

                // Act
                var result = await controller.PostTeam(teamDto);

                // Assert
                var createdAtRouteResult = Assert.IsType<CreatedAtRouteResult>(result.Result);
                Assert.Equal("GetTeamById", createdAtRouteResult.RouteName);
                Assert.NotNull(createdAtRouteResult.RouteValues);
                Assert.True(context.Teams.Any()); // Verify team was added
            }
        }

        [Fact]
        public async Task DeleteTeam_ReturnsNoContentResult_WhenTeamIsDeleted()
        {
            using (var context = new GOBContext(_options))
            {
                // Clear Context for New Test Data
                context.Teams.RemoveRange(context.Teams);
                context.SaveChanges();

                // Arrange
                context.Teams.Add(new Team { Team_ID = 1, Team_Name = "Team to Delete", Team_City = "City" });
                context.SaveChanges();

                var controller = new TeamsController(context);

                // Act
                var result = await controller.DeleteTeam(1);

                // Assert
                Assert.IsType<NoContentResult>(result);
                Assert.False(context.Teams.Any()); // Verify team was deleted
            }
        }

        [Fact]
        public async Task DeleteTeam_ReturnsNotFoundResult_WhenTeamDoesNotExist()
        {
            using (var context = new GOBContext(_options))
            {
                // Clear Context for New Test Data
                context.Teams.RemoveRange(context.Teams);
                context.SaveChanges();

                // Arrange
                var controller = new TeamsController(context);

                // Act
                var result = await controller.DeleteTeam(99);

                // Assert
                Assert.IsType<NotFoundResult>(result);
            }
        }
    }
}