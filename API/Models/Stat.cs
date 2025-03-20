namespace WebApplication1.Models
{
    using System;
    using System.Collections.Generic;

    public class Stat
    {
        public int Stat_ID { get; set; }
        public int Player_ID { get; set; }
        public int Game_ID { get; set; }
        public int Three_Points_Made { get; set; }
        public int Three_Points_Missed { get; set; }
        public int Two_Points_Made { get; set; }
        public int Two_Points_Missed { get; set; }
        public int Free_Throw_Made { get; set; }
        public int Free_Throw_Missed { get; set; }
        public int Steals { get; set; }
        public int Turnovers { get; set; }
        public int Assists { get; set; }
        public int Blocks { get; set; }
        public int Fouls { get; set; }
        public int Off_Rebounds { get; set; }
        public int Def_Rebounds { get; set; }

        // Navigation properties
        public Player Player { get; set; }
        public Game Game { get; set; }
    }

}
