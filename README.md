# Toilet seat simulator

Should we leave the seat down after going #1? This repo doesn't take a side. But hopefully, it provides some perspective in the hopes of bringing us one step closer to an answer to this age-old question.

![](https://github.com/AitanG/toilet-seat-simulation/blob/master/screenshot.png)

The observation that provided inspiration for this project was that a "lazy" policy--that is, one where everybody positions the seat only where they currently need it--is the only policy that guarantees the least number of moves. The results show a modest gain in efficiency as compared to the popular "always down" policy. However, there are other variables that factor into overall happiness, which you'll learn about readily from anyone you pose the question to. Taking the results of this simulation at face value is only recommended for cohabitants whose main concern is how many times they have to lift a two-pound toilet seat.

Feel free to clone the repo to view the animations, evaluate policies for your specific setup, and/or add your own policy!

	Lazy policy
	===========
	Adam moves: 149
	Eve moves: 109
	Average male moves: 149.0
	Average female moves: 109.0
	TOTAL MOVES: 258

	Always down policy
	==================
	Adam moves: 310
	Eve moves: 0
	Average male moves: 310.0
	Average female moves: 0.0
	TOTAL MOVES: 310
