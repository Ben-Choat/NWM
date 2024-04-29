#!/bin/bash


ls logs/* | xargs -I {} sh -c 'echo "\n\nFile: {}"; tail -n 10 {}' >> ./logs/tails.txt

