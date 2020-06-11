import { CountUp } from './countUp/dist/countUp.min';

window.onload = function() {
  var countUp = new CountUp('counter-main-users', 2000);
  countUp.start();
}
