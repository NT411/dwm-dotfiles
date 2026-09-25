/*
 * tatami.c
 *
 * Tatami layout with vanitygaps support.
 *
 * Compatible with:
 *   vanitygaps patch
 *
 * Uses:
 *   gappoh = outer horizontal gaps
 *   gappov = outer vertical gaps
 *   gappih = inner horizontal gaps
 *   gappiv = inner vertical gaps
 *
 * This version is heavily commented for learning/debugging.
 */

void
tatami(Monitor *m)
{
    unsigned int i, n;
    unsigned int mats, tc;

    /*
     * monitor geometry
     */
    int nx, ny, nw, nh;

    /*
     * temporary client geometry
     */
    int tnx, tny, tnw, tnh;

    /*
     * vanitygaps values
     */
    int oh, ov, ih, iv;

    Client *c;

    /*
     * count tiled clients
     */
    getgaps(m, &oh, &ov, &ih, &iv, &n);

    if (n == 0)
        return;

    /*
     * =====================================================
     * OUTER MONITOR AREA
     * =====================================================
     *
     * Apply OUTER gaps here.
     */

    nx = m->wx + ov;
    ny = m->wy + oh;

    nw = m->ww - (2 * ov);
    nh = m->wh - (2 * oh);

    /*
     * =====================================================
     * MASTER WINDOW
     * =====================================================
     */

    c = nexttiled(m->clients);

    /*
     * master width
     */
    if (n != 1)
        nw = (m->ww - (2 * ov) - iv) * m->mfact;
    else
        nw = m->ww - (2 * ov);

    /*
     * resize master
     */
    resize(
        c,
        nx,
        ny,
        nw - (2 * c->bw),
        nh - (2 * c->bw),
        False
    );

    /*
     * next client
     */
    c = nexttiled(c->next);

    /*
     * =====================================================
     * STACK AREA
     * =====================================================
     */

    /*
     * move stack right of master
     *
     * +iv creates inner vertical gap
     */
    nx += nw + iv;

    /*
     * remaining stack width
     */
    nw = (m->ww - (2 * ov)) - nw - iv;

    if (n > 1) {

        /*
         * tiled clients in stack
         */
        tc = n - 1;

        /*
         * number of complete 5-client mats
         */
        mats = tc / 5;

        /*
         * divide stack height
         */
        nh /= (mats + (tc % 5 > 0));

        /*
         * =================================================
         * PARTIAL MAT SECTION
         * =================================================
         */

        for (i = 0;
             c && (i < (tc % 5));
             c = nexttiled(c->next))
        {
            tnw = nw;
            tnx = nx;

            tnh = nh;
            tny = ny;

            switch (tc - (mats * 5)) {

            /*
             * =================================================
             * 1 CLIENT
             * =================================================
             */

            case 1:

                /*
                 * fills entire row
                 */
                break;

            /*
             * =================================================
             * 2 CLIENTS
             * =================================================
             */

            case 2:

                if ((i % 5) == 0) {

                    /*
                     * top
                     */
                    tnh = (nh / 2) - (ih / 2);

                } else {

                    /*
                     * bottom
                     */
                    tnh = (nh / 2) - (ih / 2);

                    tny += (nh / 2) + (ih / 2);
                }

                break;

            /*
             * =================================================
             * 3 CLIENTS
             * =================================================
             */

            case 3:

                if ((i % 5) == 0) {

                    /*
                     * top-left
                     */
                    tnw = (nw / 2) - (iv / 2);
                    tnh = ((2 * nh) / 3) - (ih / 2);

                } else if ((i % 5) == 1) {

                    /*
                     * top-right
                     */
                    tnx += (nw / 2) + (iv / 2);

                    tnw = (nw / 2) - (iv / 2);
                    tnh = ((2 * nh) / 3) - (ih / 2);

                } else {

                    /*
                     * bottom
                     */
                    tnh = (nh / 3) - (ih / 2);

                    tny += ((2 * nh) / 3) + (ih / 2);
                }

                break;

            /*
             * =================================================
             * 4 CLIENTS
             * =================================================
             */

            case 4:

                if ((i % 5) == 0) {

                    /*
                     * top
                     */
                    tnh = (nh / 4) - (ih / 2);

                } else if ((i % 5) == 1) {

                    /*
                     * left
                     */
                    tnw = (nw / 2) - (iv / 2);

                    tny += (nh / 4) + (ih / 2);

                    tnh = (nh / 2) - ih;

                } else if ((i % 5) == 2) {

                    /*
                     * right
                     */
                    tnx += (nw / 2) + (iv / 2);

                    tnw = (nw / 2) - (iv / 2);

                    tny += (nh / 4) + (ih / 2);

                    tnh = (nh / 2) - ih;

                } else {

                    /*
                     * bottom
                     */
                    tny += ((3 * nh) / 4) + (ih / 2);

                    tnh = (nh / 4) - (ih / 2);
                }

                break;
            }

            i++;

            resize(
                c,
                tnx,
                tny,
                tnw - (2 * c->bw),
                tnh - (2 * c->bw),
                False
            );
        }

        /*
         * =================================================
         * FULL 5-CLIENT MATS
         * =================================================
         */

        mats++;

        for (i = 0;
             c && (mats > 0);
             c = nexttiled(c->next))
        {
            /*
             * next row
             */
            if ((i % 5) == 0) {

                mats--;

                if (((tc % 5) > 0) || (i >= 5))
                    ny += nh + ih;
            }

            tnw = nw;
            tnx = nx;

            tnh = nh;
            tny = ny;

            switch (i % 5) {

            /*
             * =================================================
             * TOP LEFT VERTICAL
             * =================================================
             */

            case 0:

                tnw = (nw / 3) - (iv / 2);

                tnh = ((2 * nh) / 3) - (ih / 2);

                break;

            /*
             * =================================================
             * TOP RIGHT HORIZONTAL
             * =================================================
             */

            case 1:

                tnx += (nw / 3) + (iv / 2);

                tnw = ((2 * nw) / 3) - (iv / 2);

                tnh = (nh / 3) - (ih / 2);

                break;

            /*
             * =================================================
             * CENTER
             * =================================================
             */

            case 2:

                tnx += (nw / 3) + (iv / 2);

                tnw = (nw / 3) - iv;

                tny += (nh / 3) + (ih / 2);

                tnh = (nh / 3) - ih;

                break;

            /*
             * =================================================
             * BOTTOM RIGHT VERTICAL
             * =================================================
             */

            case 3:

                tnx += ((2 * nw) / 3) + (iv / 2);

                tnw = (nw / 3) - (iv / 2);

                tny += (nh / 3) + (ih / 2);

                tnh = ((2 * nh) / 3) - (ih / 2);

                break;

            /*
             * =================================================
             * BOTTOM LEFT HORIZONTAL
             * =================================================
             */

            case 4:

                tnw = ((2 * nw) / 3) - (iv / 2);

                tny += ((2 * nh) / 3) + (ih / 2);

                tnh = (nh / 3) - (ih / 2);

                break;
            }

            i++;

            /*
             * resize client
             */
            resize(
                c,
                tnx,
                tny,
                tnw - (2 * c->bw),
                tnh - (2 * c->bw),
                False
            );
        }
    }
}
