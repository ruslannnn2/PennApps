from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

text = "Erika Kirk, a graduate of Liberty University, won the Miss Arizona USA pageant in 2012 and went on to start her own podcast, clothing brand and nonprofit organization, and married the political organizer in 2021. Charlie Kirk cofounded TPUSA in 2012.\n\nShe is set to speak at a memorial for her deceased husband at State Farm Stadium in Glendale, Arizona — home to the Arizona Cardinals football team — alongside President Donald Trump, Vice President JD Vance and several senior administration officials.\n\nThe influential political organization has seen a surge in interest from young conservatives since the fatal shooting of its leader last week at a university in Utah. In the week following Charlie Kirk’s killing, the group said it had received more than 50,000 requests from high school and college students to start a chapter with the organization’s network or join an existing one.\n\nErika Kirk vowed to carry on her husband’s legacy in the wake of his death, committing to “make Turning Point the biggest thing this nation has ever seen” in public remarks just hours after authorities announced the arrest of Tyler Robinson, a 22-year-old Utah man now charged with aggravated murder."

tokenizer = AutoTokenizer.from_pretrained("bert-base-cased")

model = AutoModelForSequenceClassification.from_pretrained("bucketresearch/politicalBiasBERT")


inputs = tokenizer(text, return_tensors="pt")
labels = torch.tensor([0])
outputs = model(**inputs, labels=labels)
loss, logits = outputs[:2]

# [0] -> left 
# [1] -> center
# [2] -> right
probabilities = logits.softmax(dim=-1)[0].tolist()
print(logits.softmax(dim=-1)[0].tolist()) 

weights = [1, 5, 10] # [left, center, right]
score = round(sum(p * w for p, w in zip(probabilities, weights)), 1)

print(score)

