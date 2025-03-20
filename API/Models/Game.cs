namespace WebApplication1.Models
{
    using System;
    using System.Collections.Generic;

    public class Game
    {
        public int Game_ID { get; set; }
        public int Home_ID { get; set; }
        public int Away_ID { get; set; }
        public DateTime Game_Date { get; set; }

        // Navigation properties
        public Team HomeTeam { get; set; }
        public Team AwayTeam { get; set; }
        public ICollection<Stat> Stats { get; set; }
    }
}
