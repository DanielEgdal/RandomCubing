import java.util.Queue;
import java.util.LinkedList;
import java.util.*;

class eo3_bits {
    
    public static String db(int decimal){
        String sdb = Integer.toBinaryString(decimal);
        int lendb = sdb.length();
        if (lendb < 12){
            for (int i=0;i<12-lendb;i++){
                sdb = "0"+sdb;
            }
        }
        return sdb;
    }
    

    public static int swap2(int k, int pos1,int pos2) {
        pos1 = 11-pos1;
        pos2 = 11-pos2;
        int set1 =  (k >> pos1) & 1;
        int set2 =  (k >> pos2) & 1;
        int xor = (set1 ^ set2);
        xor = (xor << pos1) | (xor << pos2);
        return k ^ xor;
    }
    
    public static int swap_bits4(int k, int pos1,int pos2,int pos3,int pos4) {
        pos1 = 11-pos1;
        pos2 = 11-pos2;
        pos3 = 11-pos3;
        pos4 = 11-pos4;
        int set1 =  (k >> pos1) & 1;
        int set2 =  (k >> pos2) & 1;
        int set3 =  (k >> pos3) & 1;
        int set4 =  (k >> pos4) & 1;
        // int xor = (set1 ^ set2);
        int xor = (set1 << pos4) | (set2 << pos1) | (set3 << pos2) | (set4 << pos3);
        int resetter = (1 << pos4) | (1 << pos1) | (1 << pos2) | (1 << pos3);
        // System.out.println(xor);
        // System.out.println(resetter);
        // System.out.println(~resetter+4096);
        return ((~resetter+4096)&k) | xor;
    }
    // // String scramble ="U R2 F B R B2 R U2 L B2 R U' D' R2 F R' L B2 U2 F2";

    public static int swap_bits1(int k, int pos1,int pos2,int pos3,int pos4) {
        return swap2(swap2(swap2(k, pos1, pos2),pos2,pos3),pos3,pos4);
    }

    public static int F(int k){
        int mask = 15;
        int inv_mask = (k >> 4) << 4;
        int temp1 = ((k&mask)^mask) + inv_mask;
        return swap_bits1(temp1,11,10,9,8);
    }
    
    public static int Fp(int k){
        int mask = 15;
        int inv_mask = (k >> 4) << 4;
        int temp1 = ((k&mask)^mask) + inv_mask;
        return swap_bits1(temp1,8,9,10,11);
        }

    public static int B(int k){
        int mask = 240;
        int inv_mask = 3855 & k;
        int temp1 = ((k&mask)^mask) + inv_mask;
        return swap_bits1(temp1,7,6,5,4);
    }

    public static int Bp(int k){
        int mask = 240;
        int inv_mask = 3855 & k;
        int temp1 = ((k&mask)^mask) + inv_mask;
        return swap_bits1(temp1,4,5,6,7);
    }

    public static int R(int k){
        return swap_bits1(k,3,11,2,7);
    }

    public static int Rp(int k){
        return swap_bits1(k,7,2,11,3);
    }
    public static int L(int k){
        return swap_bits1(k,9,1,5,0);
    }

    public static int Lp(int k){
        return swap_bits1(k,0,5,1,9);
    }

    public static int U(int k){
        return swap_bits1(k,1,10,3,4);
    }

    public static int Up(int k){
        return swap_bits1(k,4,3,10,1);
    }

    public static int D(int k){
        return swap_bits1(k,0,6,2,8);
    }

    public static int Dp(int k){
        return swap_bits1(k,8,2,6,0);
    }

    public static int D2(int k){
        return swap2(swap2(k,0,2),8,6);
    }

    public static int U2(int k){
        return swap2(swap2(k,1,3),10,4);
    }

    public static int R2(int k){
        return swap2(swap2(k,11,7),2,3);
    }

    public static int L2(int k){
        return swap2(swap2(k,0,1),9,5);
    }

    public static int F2(int k){
        return swap2(swap2(k,11,9),8,10);
    }

    public static int B2(int k){
        return swap2(swap2(k,4,6),7,5);
    }

    public static int perform_move(String move, int k){
        int tempk = 0;
        if (move.equals("U'")){
            tempk = Up(k);
        }
        else if (move.equals("U")){
            tempk = U(k);
        }
        else if (move.equals("R'")){
            tempk = Rp(k);
        }
        else if (move.equals("R")){
            tempk = R(k);
        }
        else if (move.equals("D'")){
            tempk = Dp(k);
        }
        else if (move.equals("D")){
            tempk = D(k);
        }
        else if (move.equals("L")){
            tempk = L(k);
        }
        else if (move.equals("L'")){
            tempk = Lp(k);
        }
        else if (move.equals("L2")){
            tempk = L2(k);
        }
        else if (move.equals("R2")){
            tempk = R2(k);
        }
        else if (move.equals("U2")){
            tempk = U2(k);
        }
        else if (move.equals("D2")){
            tempk = D2(k);
        }
        else if (move.equals("U2")){
            tempk = U2(k);
        }
        else if (move.equals("B2")){
            tempk = B2(k);
        }
        else if (move.equals("F2")){
            tempk = F2(k);
        }
        else if (move.equals("F")){
            tempk = F(k);
        }
        else if (move.equals("F'")){
            tempk = Fp(k);
        }
        else if (move.equals("B")){
            tempk = B(k);
        }
        else if (move.equals("B'")){
            tempk = Bp(k);
        }
    return tempk;
    }

    public static ArrayList<String> solve(int k){
        String[] possmoves = {"U", "U'","U2","R2", "R", "R'","L2", "L", "L'","B2", "B","B'","D2","D","D'","F2","F","F'"};
        Queue<Object[]> q = new LinkedList<>();
        Set<Integer> visited = new HashSet<Integer>();
        ArrayList<String> start_move_list = new ArrayList<String>();
        Object init_start[] = {k,start_move_list,"hn"};
        q.add(init_start);
        boolean solved = false;
        ArrayList<String> the_solution2 = new ArrayList<String>();
        while (!solved){
            Object stuff[] = q.remove();
            int state = (Integer) stuff[0];
            ArrayList<String> solution_so = (ArrayList<String>) stuff[1];
            // String solution_so[] = (String[]) stuff[1];
            String last_move = (String) stuff[2];
            boolean success = visited.add(state);
            if (success){
                for (String movev:possmoves){
                    ArrayList<String> temp_sol = new ArrayList<String>(solution_so);
                    if (movev.charAt(0) != last_move.charAt(0)){
                        int new_state = perform_move(movev,state);
                        temp_sol.add(movev);
                        // String new_sol[] = solution_so + (String[]) movev;
                        if (new_state == 4095){
                            solved = true;
                            for (String movevv:temp_sol){
                                the_solution2.add(movevv);
                            }
                            break;
                        }
                        else{
                            Object to_append[] = {new_state,temp_sol,movev};
                            q.add(to_append);
                        }
                    }
                }
            }
            // System.out.println(k, move_list,start_move);
        }
        return the_solution2;
    }
    public static void main(String args[]){
        Scanner sc = new Scanner(System.in);
        String scramble = sc.nextLine();
        // System.out.println(scramble);
        long startTime = System.currentTimeMillis();
        for (int i=0;i<101;i++){
            int starting_pos = 4095;
            // String scramble = "D B2 R U' F2 L B U F R' D2 R2 D R2 L2 D' B2 U' F2 U' L2";
            // String scramble ="U R2 F B R B2 R U2 L B2 R U' D' R2 F R' L B2 U2 F2";
            String[] splitted = scramble.split(" ");
            for (String movess:splitted){
                starting_pos = perform_move(movess, starting_pos);
                // System.out.println(movess +" "+ db(starting_pos));
            }
            ArrayList<String> solutionpls = solve(starting_pos);

            // System.out.println(solutionpls);
        }

        long endTime = System.currentTimeMillis();

        System.out.println("That took " + (endTime - startTime) + " milliseconds");
    }
   }