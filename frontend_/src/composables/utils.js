function areStringsIdentical(str1, str2) {
    // NOTE that this is a simplified approach to check the similarity of two strings
    // for more accurate results use the Levenshtein distance...

    function getCharFrequency(str) {
        const freq = {};
        for (const char of str) {
            if (freq[char]) {
                freq[char]++;
            } else {
                freq[char] = 1;
            }
        }
        return freq;
    };
    const freq1 = getCharFrequency(str1);
    const freq2 = getCharFrequency(str2);

    let totalChars = 0;
    let matchingChars = 0;

    for (const char in freq1) {
        totalChars += freq1[char];
        if (freq2[char]) {
            matchingChars += Math.min(freq1[char], freq2[char]);
        }
    }

    for (const char in freq2) {
        if (!freq1[char]) {
            totalChars += freq2[char];
        }
    }

    const similarity = matchingChars / totalChars;
    // console.log(`Labels are ${similarity*100} % similar.`)
    return similarity >= 0.85;
}

function findBestMatchIndex(list, searchLabel) {
    let bestMatchIndex = -1;
    let bestMatchScore = 0;

    // Iterate through the list
    for (let i = 0; i < list.length; i++) {
        const currentLabel = list[i].label;

        // Use the areStringsIdentical function for similarity checking
        const similarity = areStringsIdentical(searchLabel, currentLabel);

        // If a better match is found, update the index and match score
        if (similarity > bestMatchScore) {
            bestMatchIndex = i;
            bestMatchScore = similarity;
        }
    }

    // If bestMatchScore is above the threshold, return the index, else return -1
    return bestMatchScore >= 0.85 ? bestMatchIndex : -1;
}

export{
    findBestMatchIndex
}