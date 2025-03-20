namespace WebApplication1.Database
{
    using Microsoft.EntityFrameworkCore;
    using WebApplication1.Models;

    public class MyDbContext : DbContext
    {
        public MyDbContext(DbContextOptions<MyDbContext> options) : base(options) { }

        public DbSet<Game> Games { get; set; }
        public DbSet<Player> Players { get; set; }
        public DbSet<Stat> Stats { get; set; }
        public DbSet<Team> Teams { get; set; }

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            modelBuilder.Entity<Game>()
                .HasOne(g => g.HomeTeam)
                .WithMany(t => t.HomeGames)
                .HasForeignKey(g => g.Home_ID);

            modelBuilder.Entity<Game>()
                .HasOne(g => g.AwayTeam)
                .WithMany(t => t.AwayGames)
                .HasForeignKey(g => g.Away_ID);

            modelBuilder.Entity<Player>()
                .HasOne(p => p.Team)
                .WithMany(t => t.Players)
                .HasForeignKey(p => p.Team_ID);

            modelBuilder.Entity<Stat>()
                .HasOne(s => s.Player)
                .WithMany(p => p.Stats)
                .HasForeignKey(s => s.Player_ID);

            modelBuilder.Entity<Stat>()
                .HasOne(s => s.Game)
                .WithMany(g => g.Stats)
                .HasForeignKey(s => s.Game_ID);

        }
    }
}
