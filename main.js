import Transport from "@ledgerhq/hw-transport-node-hid";
import Eth from "@ledgerhq/hw-app-eth";

var args = process.argv.slice(2);
const index = args[0];
const unsigned_tx = args[1];


Transport.create().then(transport => {
    const eth = new Eth(transport);
    eth.signTransaction(`44'/60'/${index}'/0/0`, unsigned_tx).then(result => {
        console.log(`v: ${result['v']}`);
        console.log(`r: ${result['r']}`);
        console.log(`s: ${result['s']}`);
    }).catch(error => {
        console.log(error);}
    );
}).catch(error => {
    console.log(error);
});
