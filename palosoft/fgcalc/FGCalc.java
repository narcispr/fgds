import java.util.Objects;
import java.util.Map;
import java.util.Vector;

import Weapon;
import Mini;

public class FGCalc {
    Map< String, Vector<Mini> > warbands;

    public FGCalc() {
    }

    public FGCalc(Map<String,Vector<Mini>> warbands) {
        this.warbands = warbands;
    }

    public Map<String,Vector<Mini>> getWarbands() {
        return this.warbands;
    }

    public void setWarbands(Map<String,Vector<Mini>> warbands) {
        this.warbands = warbands;
    }

    public FGCalc warbands(Map<String,Vector<Mini>> warbands) {
        this.warbands = warbands;
        return this;
    }

    @Override
    public boolean equals(Object o) {
        if (o == this)
            return true;
        if (!(o instanceof FGCalc)) {
            return false;
        }
        FGCalc fGCalc = (FGCalc) o;
        return Objects.equals(warbands, fGCalc.warbands);
    }

    @Override
    public int hashCode() {
        return Objects.hashCode(warbands);
    }

    @Override
    public String toString() {
        return "{" +
            " warbands='" + getWarbands() + "'" +
            "}";
    }

    public boolean loadFromJson(String path){
        return true;
    }
}