import torch
from get_data import tokenizer1
from torch.autograd import Variable
from chatspace import ChatSpace
spacer = ChatSpace()

def inference(device, args, TEXT, LABEL, model, sa_model):
    from KoBERT.SBT_main import bert_inference
    sentence = input("문장을 입력하세요 : ")
    se_list = [sentence]

    # https://github.com/SKTBrain/KoBERT
    # SKT 에서 공개한 KoBert Sentiment Analysis 를 통해 입력문장의 긍정 부정 판단.
    sa_label = int(bert_inference(sa_model, se_list))

    sa_token = ''
    # SA Label 에 따른 encoder input 변화.
    if sa_label == 0:
        sa_token = TEXT.vocab.stoi['<nega>']
    else:
        sa_token = TEXT.vocab.stoi['<posi>']

    enc_input = tokenizer1(sentence)
    enc_input_index = []

    # encoder input string to index tensor and plus <pad>
    for tok in enc_input:
        enc_input_index.append(TEXT.vocab.stoi[tok])
    enc_input_index.append(sa_token)
    for j in range(args.max_len - len(enc_input_index)):
        enc_input_index.append(TEXT.vocab.stoi['<pad>'])

    enc_input_index = Variable(torch.LongTensor([enc_input_index]))

    dec_input = torch.LongTensor([[LABEL.vocab.stoi['<sos>']]])
    print("긍정" if sa_label == 1 else "부정")

    model.eval()
    pred = []
    for i in range(args.max_len):
        y_pred = model(enc_input_index.to(device), dec_input.to(device))
        y_pred_ids = y_pred.max(dim=-1)[1]
        if (y_pred_ids[0, -1] == LABEL.vocab.stoi['<eos>']):
            y_pred_ids = y_pred_ids.squeeze(0)
            print(">", end=" ")
            for idx in range(len(y_pred_ids)):
                if LABEL.vocab.itos[y_pred_ids[idx]] == '<eos>':
                    pred_sentence = "".join(pred)
                    pred_str = spacer.space(pred_sentence)
                    print(pred_str)
                    break
                else:
                    pred.append(LABEL.vocab.itos[y_pred_ids[idx]])
            return 0

        dec_input = torch.cat(
            [dec_input.to(torch.device('cpu')),
             y_pred_ids[0, -1].unsqueeze(0).unsqueeze(0).to(torch.device('cpu'))], dim=-1)
    return 0