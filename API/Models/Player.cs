namespace WebApplication1.Models
{
    using System;
    using System.Collections.Generic;
    using System.ComponentModel.DataAnnotations;

    public class Player
    {
        [Key]
        public int Player_ID { get; set; }
        public int? Team_ID { get; set; } // Nullable because it can be null
        public string First_Name { get; set; }
        public string Last_Name { get; set; }
        public string Position_ID { get; set; }
        public int Jersy_Number { get; set; }

        // Navigation properties
        public Team Team { get; set; }
        public ICollection<Stat> Stats { get; set; }
    }
}
