class player{
    int id;
    int position;
    int a;
    void printId() {
        printlnInt(id);
    }
}

class team{
    player []players;// = new player[6];

    team() {
        players = new player[6];
        int i;
        for (i = 0; i < 6; i++) 
            players[i] = new player();
    }
    void print_position(int i){
        printInt(this.players[i].position);
    }

}

public class objects{
    public static void main(){
        team RCB = new team();
        //player a = new player();
        //player b = new player();
        //a.id = 5;
        //b.id = 6;
        RCB.players[2].id = 5;
        RCB.players[2].position = 6;
        RCB.print_position(2);
        //printlnInt(a.id);
        //printlnInt(b.id);
    }

}
