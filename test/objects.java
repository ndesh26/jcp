class player{
    int id;
}

class team{
    player players[] = new player[6];
}

public class objects{
    public static void main(){
        team RCB;// = new team();
        RCB.players[1].id = 1;
        //RCB.players[1].position = 6;
        //printInt(RCB.players[1].id);
        //printInt(RCB.players[1].position);
    }
}
