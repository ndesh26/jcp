class player{
    int id;
    int position;
}

class team{
    player []players = new player[6];

    void print_position(int i){
        printInt(this.players[0].position);
    }

}

public class objects{
    public static void main(){
        team RCB;// = new team();
        RCB.players[2].id = 5;
        RCB.players[1].position = 6;
        RCB.print_position();
    }
}
