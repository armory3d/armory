package armory.logicnode;
import armory.trait.internal.CanvasScript;

class HideActiveCanvas extends LogicNode 
{

    public function new(tree:LogicTree) 
    {
        super(tree);
    }

    override function run(from: Int) 
    {
        //get bool from socket
        var value = inputs[1].get(); 
        CanvasScript.getActiveCanvas().setCanvasVisibility(value);

        // Execute next action linked to this node, this activates the output socket at position/index 0
        runOutput(0);
    }
}