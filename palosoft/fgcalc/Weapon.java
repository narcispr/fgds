package palosoft.fgcalc;
import java.util.Objects;
import java.io.IOException;
import org.json.simple.JSONObject;
 
public class Weapon {
    String name;
    int range;
    int damageMod;
    int armourMod;

    public Weapon() {
        this.name = "Weapon";
        this.range = 0;
        this.damageMod = 0;
        this.armourMod = 0; 
    }

    public Weapon(final String name, final int range, final int damage_mod, final int armour_mod) {
        this.name = name;
        this.range = range;
        this.damageMod = damage_mod;
        this.armourMod = armour_mod;
    }

    public String getName() {
        return this.name;
    }

    public void setName(final String name) {
        this.name = name;
    }

    public int getRange() {
        return this.range;
    }

    public void setRange(final int range) {
        this.range = range;
    }

    public int getDamageMod() {
        return this.damageMod;
    }

    public void setDamageMod(final int damageMod) {
        this.damageMod = damageMod;
    }

    public int getArmourMod() {
        return this.armourMod;
    }

    public void setArmourMod(final int armourMod) {
        this.armourMod = armourMod;
    }

    public Weapon name(String name) {
        this.name = namfinal String name) {
        this.name = name;
        return this;
    }

    public Weapon range(final int range) {
        this.range = range;
        return this;
    }

    public Weapon damageMod(final int damageMod) {
        this.damageMod = damageMod;
        return this;
    }

    public Weapon armourMod(final int armourMod) {
        this.armourMod = armourMod;
        return this;
    }

    @Override
    public boolean equals(final Object o) {
        if (o == this)
            return true;
        if (!(o instanceof Weapon)) {
            return false;
        }
        final Weapon weapon = (Weapon) o;
        return Objects.equals(name, weapon.name) && range == weapon.range && damageMod == weapon.damageMod
                && armourMod == weapon.armourMod;
    }

    @Override
    public int hashCode() {
        return Objects.hash(name, range, damageMod, armourMod);
    }

    public String toString() {
        String r = "CC";
        if (getRange() > 0) {
            r = Integer.toString(getRange());
        }
        String dm = "";
        if (getDamageMod() != 0) {
            dm = Integer.toString(getDamageMod());
        }
        String am = "";
        if (getArmourMod() != 0) {
            am = Integer.toString(getArmourMod());
        }

        return String.format("%s %s %s %s", getName(), r, dm, am);
    }

    public JSONObject getJSON() {
        final weapon.put("name", getName());
        weapon.put("range", getRange());
        weapon.put("damage_mod", getDamageMod());
        weapon.put("armour_mod", getArmourMod());
        return weapon;
    }
            
    public static void main(final String[] args) {
        final Weapon w = new Weapon("Staff", 0, -1, -1);
        System.out.println(w);
        System.out.println(w.getJSON().toString());
    }
}
