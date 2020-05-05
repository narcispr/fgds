import java.util.Objects;
import java.util.Vector;
import Weapon;

public class Mini {
    enum MiniType {
        Wizard,
        Apprentice,
        Soldier,
        Creature
    }
    enum WizardFamily {
        None,
        Elementalist,
        Enchanter,
        Witch
    }
      
    String name;
    MiniType miniType;
    WizardFamily family;
    int M;
    int F;
    int S;
    int A;
    int W;
    int H;
    Vector<Weapon> weapons;

    public Mini() {
        this.name = "Mini";
        this.miniType = MiniType.Creature;
        this.family = WizardFamily.None;
        this.M = 6;
        this.F = 0;
        this.S = 0;
        this.A = 10;
        this.W = 0;
        this.H = 1;
    }

    public Mini(final String name, final MiniType miniType, final WizardFamily family, final int M, final int F,
            final int S, final int A, final int W, final int H, final Vector<Weapon> weapons) {
        this.name = name;
        this.miniType = miniType;
        this.family = family;
        this.M = M;
        this.F = F;
        this.S = S;
        this.A = A;
        this.W = W;
        this.H = H;
        this.weapons = weapons;
    }

    public Mini(final String name, final MiniType miniType, final WizardFamily family, final int M, final int F,
            final int S, final int A, final int W, final int H) {
        this.name = name;
        this.miniType = miniType;
        this.family = family;
        this.M = M;
        this.F = F;
        this.S = S;
        this.A = A;
        this.W = W;
        this.H = H;
        this.weapons = new Vector<Weapon>();
    }

    public String getName() {
        return this.name;
    }

    public void setName(final String name) {
        this.name = name;
    }

    public MiniType getMiniType() {
        return this.miniType;
    }

    public void setMiniType(final MiniType miniType) {
        this.miniType = miniType;
    }

    public WizardFamily getFamily() {
        return this.family;
    }

    public void setFamily(final WizardFamily family) {
        this.family = family;
    }

    public int getM() {
        return this.M;
    }

    public void setM(final int M) {
        this.M = M;
    }

    public int getF() {
        return this.F;
    }

    public void setF(final int F) {
        this.F = F;
    }

    public int getS() {
        return this.S;
    }

    public void setS(final int S) {
        this.S = S;
    }

    public int getA() {
        return this.A;
    }

    public void setA(final int A) {
        this.A = A;
    }

    public int getW() {
        return this.W;
    }

    public void setW(final int W) {
        this.W = W;
    }

    public int getH() {
        return this.H;
    }

    public void setH(final int H) {
        this.H = H;
    }

    public Vector<Weapon> getWeapons() {
        return this.weapons;
    }

    public void setWeapons(final Vector<Weapon> weapons) {
        this.weapons = weapons;
    }

    public Mini name(final String name) {
        this.name = name;
        return this;
    }

    public Mini mini_type(final MiniType mini_type) {
        this.miniType = mini_type;
        return this;
    }

    public Mini family(final WizardFamily family) {
        this.family = family;
        return this;
    }

    public Mini M(final int M) {
        this.M = M;
        return this;
    }

    public Mini F(final int F) {
        this.F = F;
        return this;
    }

    public Mini S(final int S) {
        this.S = S;
        return this;
    }

    public Mini A(final int A) {
        this.A = A;
        return this;
    }

    public Mini W(final int W) {
        this.W = W;
        return this;
    }

    public Mini H(final int H) {
        this.H = H;
        return this;
    }

    public Mini weapons(final Vector<Weapon> weapons) {
        this.weapons = weapons;
        return this;
    }

    @Override
    public boolean equals(final Object o) {
        if (o == this)
            return true;
        if (!(o instanceof Mini)) {
            return false;
        }
        final Mini mini = (Mini) o;
        return Objects.equals(name, mini.name) && Objects.equals(miniType, mini.miniType) && Objects.equals(family, mini.family) && M == mini.M && F == mini.F && S == mini.S && A == mini.A && W == mini.W && H == mini.H && Objects.equals(weapons, mini.weapons);
    }

    @Override
    public int hashCode() {
        return Objects.hash(name, miniType, family, M, F, S, A, W, H, weapons);
    }

    @Override
    public String toString() {
        return "{" +
            " name='" + getName() + "'" +
            ", mini_type='" + getMiniType() + "'" +
            ", family='" + getFamily() + "'" +
            ", M='" + getM() + "'" +
            ", F='" + getF() + "'" +
            ", S='" + getS() + "'" +
            ", A='" + getA() + "'" +
            ", W='" + getW() + "'" +
            ", H='" + getH() + "'" +
            ", weapons='" + getWeapons() + "'" +
            "}";
    }

    public static void main(final String[] args) {
        final Weapon w = new Weapon("Staff", 0, -1, -1);
        final Mini m = new Mini("Marfaro", MiniType.Wizard, WizardFamily.Enchanter, 6, 2, 0, 10, 4, 14);
        m.weapons.add(w);
        System.out.println(m);
    }
}
