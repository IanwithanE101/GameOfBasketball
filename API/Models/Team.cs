namespace WebApplication1.Models
{
    using System;
    using System.Collections.Generic;

    public class Team
    {
        public int Team_ID { get; set; }
        public string Team_Name { get; set; }
        public string Team_City { get; set; }

        // Navigation properties
        public ICollection<Player> Players { get; set; }
        public ICollection<Game> HomeGames { get; set; } // Games where this team is home
        public ICollection<Game> AwayGames { get; set; } // Games where this team is away
    }
}
